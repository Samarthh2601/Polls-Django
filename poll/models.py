from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count  


class Poll(models.Model):
    text = models.CharField(max_length=512)
    pub_date = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    # end_date = models.DateTimeField()

    @property
    def is_active(self) -> bool:
        return self.active

    def __str__(self) -> str:
        return self.text

    @property
    def get_vote_count(self) -> dict:
        choices_with_vote_counts = self.choices.annotate(vote_count=Count('votes'))
        result = {choice.text: choice.vote_count for choice in choices_with_vote_counts}
        return result

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.text[:15]} | {self.poll.text[:15]}"


class Vote(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.username} | {self.choice.text[:15]} | {self.choice.poll.text[:15]}"