from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Poll, Choice, Vote
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def get_choice_obj(request: HttpRequest, use_id=True):
    choice_voted = request.POST.get("selected_choice") # Get the selected choice text from the hidden input [poll/display_polls.html]
    key = request.POST.get("poll_key") #Get the primary key of the selected poll from the hidden input [poll/display_polls.html]
    choice_id = request.POST.get("selected_choice_id")

    poll = Poll.objects.get(pk=key) 

    if not poll:
        messages.error(request, "Error occurred. Please ensure that the poll exists.")
        return False
        
    if poll.end_date <= timezone.now():
        messages.error(request, "Poll has already ended.")
        return False
    
    if use_id is True:
        choice = Choice.objects.get(pk=choice_id) # Get selected choice object from db
    else: choice = Choice.objects.get(pk=choice_voted, poll=poll)

    return choice


# Displays all the polls from the database
@login_required
def display_polls(request: HttpRequest):
    return render(request, 'poll/display_polls.html', context={"polls": Poll.objects.all()})


@login_required
def create_poll(request: HttpRequest):
    if request.method == "POST":
        question = request.POST.get("question")
        deadline = request.POST.get("deadline")
        choices = request.POST.getlist("choices")

        # Validate the number of choices
        if len(choices) < 2 or len(choices) > 4:
            messages.error(request, "You must provide between 2 and 4 choices.")
            return redirect("create_poll")

        try:
            # Parse and validate the deadline
            deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M")

        except ValueError as e:
            messages.error(request, "Invalid deadline!")
            return redirect('create_poll')

        # Create the poll and choices
        poll = Poll.objects.create(text=question, end_date=deadline, owner=request.user)
        for choice_text in choices:
            Choice.objects.create(poll=poll, text=choice_text)

        messages.success(request, "Poll created!")
        return redirect("display_polls")  # Redirect to a list of polls (update as needed)

    return render(request, "poll/create_poll.html")


@login_required
def my_polls(request: HttpRequest):
    # Get filtered polls
    polls = Poll.objects.filter(owner=request.user)
    if not polls:
        messages.warning(request, "You have not created any polls yet")
        return redirect("create_poll")

    return render(request, 'poll/my_polls.html', context={"polls": polls})

@login_required
def delete_poll(request: HttpRequest):
    poll_key = request.GET.get("poll_key")
    if poll_key is None:
        messages.error(request, "Invalid poll detected")
        return redirect("my_polls")
    
    poll = Poll.objects.get(pk=poll_key)
    if poll.owner != request.user:
        messages.error("You are not the owner of that poll")
        return redirect("display_polls")
    poll.delete()
    return redirect("my_polls")

def add_vote(request: HttpRequest):
    choice = get_choice_obj(request)

    if choice is False:
        return redirect("display_polls")    
    
    Vote.objects.get_or_create(choice=choice, user=request.user)

    messages.success(request, "Successfully voted!")
    return redirect("display_polls")

@login_required
def my_votes(request: HttpRequest):
    if request.method == "GET":
        votes = Vote.objects.filter(user=request.user)    
        if not votes.exists():
            messages.error(request, "You have not voted yet!")
            return redirect("display_polls")

        choices = {vote.choice.pk: vote.choice for vote in votes}
        return render(request, 'poll/my_votes.html', context={"choices": choices})
    
    choice = get_choice_obj(request)

    if choice is False:
        return redirect("my_votes")
    
    vote = Vote.objects.get(choice=choice, user=request.user)
    vote.delete()
    messages.success(request, "Successfully deleted!")
    return redirect("my_votes")