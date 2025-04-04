from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest

from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Poll, Choice, Vote
from .forms import PollUpdateForm, ChoiceUpdateForm
from django.forms import modelformset_factory

from datetime import datetime
from django.core.paginator import Paginator

# Helper function for add_vote and my_votes views
def get_choice_obj(request: HttpRequest, use_id=True):
    choice_voted = request.POST.get("selected_choice") # Get the selected choice text from the hidden input [poll/display_polls.html]
    key = request.POST.get("poll_key") #Get the primary key of the selected poll from the hidden input [poll/display_polls.html]
    choice_id = request.POST.get("selected_choice_id")

    poll = Poll.objects.get(pk=key) 

    if not poll:
        messages.error(request, "Error occurred. Please ensure that the poll exists.")
        return False
    
    if not choice_id:
        messages.error(request, "Please select your vote")
        return False

    if poll.end_date <= timezone.now():
        messages.error(request, "Poll has already ended.")
        return False
    
    if use_id is True:
        choice = Choice.objects.get(pk=choice_id) # Get selected choice object from db
    else: choice = Choice.objects.get(pk=choice_voted, poll=poll)

    return choice

# Helper function for edit_poll, delete_poll and view_poll views
def get_valid_poll(request, poll_key: int) -> Poll | bool:
    if poll_key is None:
        messages.error(request, "Invalid poll detected")
        return False

    poll = Poll.objects.get(pk=poll_key)

    if poll.owner != request.user: #Check owner
        messages.error("You are not the owner of that poll")
        return False
    
    return poll

# ---------------------------------------------------------------------
# POLL CRUD VIEWS


@login_required
def display_polls(request: HttpRequest):
    polls = (Poll.get_polls().order_by("-pub_date")) #Reversing the list to make new polls appear on top

    paginator = Paginator(polls, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'poll/display_polls.html', context={"page_obj": page_obj})

@login_required
def display_expired_polls(request: HttpRequest):
    polls = polls = Poll.get_polls(active=False).order_by("-pub_date")

    paginator = Paginator(polls, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'poll/display_polls.html', context={"page_obj": page_obj})


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
            deadline = timezone.make_aware(datetime.strptime(deadline, "%Y-%m-%dT%H:%M"))

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
def edit_poll(request: HttpRequest):
    poll_key = request.GET.get("poll_key") #Get the poll id from my_polls.html
    poll = get_valid_poll(request, poll_key)

    if poll is False:
        return redirect("my_polls")

    choices = Choice.objects.filter(poll=poll)
    ChoiceFormSet = modelformset_factory(Choice, form=ChoiceUpdateForm, extra=0)

    if request.method == "GET":
        formset = ChoiceFormSet(queryset=choices)
        return render(request, 'poll/edit_poll.html', {'form': PollUpdateForm(instance=poll), 'formset': formset})
    

    form = PollUpdateForm(request.POST, instance=poll)
    formset = ChoiceFormSet(request.POST, queryset=choices)

    if form.is_valid() and formset.is_valid():
        form.save()
        formset.save()
        messages.success(request, f'Poll updated!')
        return redirect("my_polls")
        
    else:
        messages.warning(request, form.errors)
        return redirect('my_polls')


@login_required
def delete_poll(request: HttpRequest):
    poll_key = request.GET.get("poll_key") #Get the poll id from my_polls.html
    poll = get_valid_poll(request, poll_key)

    if poll is False:
        return redirect("my_polls")

    poll.delete()
    return redirect("my_polls")

@login_required
def view_poll(request: HttpRequest):
    poll_key = request.GET.get("poll_key")
    poll = get_valid_poll(request, poll_key)
    
    if poll is False:
        return redirect("display_polls")

    expired = True if poll.end_date <= timezone.now() else False

    return render(request, "poll/view_poll.html", context={"poll": poll, "expired": expired})

# --------------USER SPECIFIC VIEWS-------------------------

@login_required
def my_polls(request: HttpRequest):
    # Get filtered polls
    polls = Poll.objects.filter(owner=request.user).order_by('-pub_date')

    if not polls:
        messages.warning(request, "You have not created any polls yet")
        return redirect("create_poll")

    paginator = Paginator(polls, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'poll/my_polls.html', context={"page_obj": page_obj})

@login_required
def my_votes(request: HttpRequest):
    if request.method == "GET":
        votes = Vote.objects.filter(user=request.user)
        if not votes.exists():
            messages.error(request, "You have not voted yet!")
            return redirect("display_polls")

        choices = {vote.choice.pk: vote.choice for vote in votes}

        paginator = Paginator(list(choices.items()), 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'poll/my_votes.html', context={"page_obj": page_obj})
    
    choice = get_choice_obj(request) #Get the Choice object from the database

    if choice is False:
        return redirect("my_votes") # If choice is not found in the database 
    
    vote = Vote.objects.get(choice=choice, user=request.user)
    vote.delete()
    messages.success(request, "Successfully deleted!")
    return redirect("my_votes")

@login_required
def add_vote(request: HttpRequest):
    choice = get_choice_obj(request) #Get the Choice object from the database

    if choice is False:
        return redirect("display_polls") # If choice is not found in the database 

    check = Vote.objects.filter(user=request.user, poll=choice.poll)
    if check:
        messages.error(request, "You have already voted in this poll. To vote again, please delete the current vote")
        return redirect("display_polls")
    
    Vote.objects.create(choice=choice, user=request.user, poll=choice.poll) #Prevents multiple votes from the same user

    messages.success(request, "Successfully voted!")
    return redirect("display_polls")

@login_required
def search(request: HttpRequest):
    if request.method == "GET":
        search_type = request.GET.get("search_type")

        search_query = request.GET.get("search_query")
        if not search_query or not search_type:
            messages.error(request, "Please enter a valid query")
            return redirect("display_polls")

        if search_type == "poll":
            polls = Poll.objects.filter(text__icontains=search_query).order_by("-pub_date")

        elif search_type == "choice":
            polls = Poll.objects.filter(choices__text__icontains=search_query).distinct().order_by("-pub_date")
        
        elif search_type == "user":
            polls = Poll.objects.filter(owner__username__icontains=search_query).order_by("-pub_date")

        paginator = Paginator(polls, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'poll/display_polls.html', context={"page_obj": page_obj})
    else:
        messages.error(request, "Invalid request method")
        return redirect("display_polls")