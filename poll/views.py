from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .models import Poll, Choice
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    polls = Poll.objects.filter(owner=request.user)
    if not polls:
        messages.warning(request, "You have not created any polls yet")
        return redirect("create_poll")

    return render(request, 'poll/display_polls.html', context={"polls": polls})