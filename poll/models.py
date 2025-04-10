from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
from django.core.exceptions import ValidationError


class Poll(models.Model):
    text = models.CharField(max_length=512)
    pub_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    end_date = models.DateTimeField()

    
    def __str__(self) -> str:
        return self.text


    def get_vote_count(self) -> dict:
        choices_with_vote_counts = self.choices.annotate(vote_count=Count('votes'))
        total_votes = sum(choice.vote_count for choice in choices_with_vote_counts)
        
        result = {}
        for choice in choices_with_vote_counts:
            percentage = (choice.vote_count / total_votes * 100) if total_votes > 0 else 0
            result[str(choice.pk)] = [choice.text, choice.vote_count, round(percentage, 2)]
        
        return result

    
    @staticmethod
    def get_polls(active=True):
        if active is True:
            return Poll.objects.filter(end_date__gt=timezone.now())
        return Poll.objects.filter(end_date__lt=timezone.now())
    

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=512)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.text[:15]} | {self.poll.text[:15]}"


class Vote(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} | {self.choice.text[:15]} | {self.choice.poll.text[:15]}"