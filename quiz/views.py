from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Attempt, AttemptAnswer, Category, Quiz

# Extra seconds allowed after the deadline (network delay, slow phones)
GRACE_SECONDS = 15


def register(request):
    if request.user.is_authenticated:
        return redirect("quiz_list")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Account created. Pick a quiz and start!")
        return redirect("quiz_list")
    return render(request, "registration/register.html", {"form": form})


def quiz_list(request):
    quizzes = (
        Quiz.objects.filter(is_published=True)
        .annotate(num_questions=Count("questions"))
        .filter(num_questions__gt=0)
        .select_related("category")
    )
    search = request.GET.get("q", "").strip()
    category_id = request.GET.get("category", "")
    if search:
        quizzes = quizzes.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if category_id.isdigit():
        quizzes = quizzes.filter(category_id=int(category_id))

    context = {
        "quizzes": quizzes,
        "categories": Category.objects.all(),
        "search": search,
        "selected_category": category_id,
    }
    return render(request, "quiz/quiz_list.html", context)


def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    best = None
    if request.user.is_authenticated:
        best = Attempt.objects.filter(
            user=request.user, quiz=quiz, finished_at__isnull=False
        ).aggregate(best=Max("score"))["best"]
    context = {
        "quiz": quiz,
        "num_questions": quiz.questions.count(),
        "best": best,
    }
    return render(request, "quiz/quiz_detail.html", context)


def grade_attempt(attempt, selected):
    """Mark an attempt as finished and save the score.

    selected = {question_id: choice_id}. Unanswered questions score 0.
    """
    questions = attempt.quiz.questions.prefetch_related("choices")
    answers = []
    score = 0
    for question in questions:
        chosen = None
        choice_id = selected.get(question.id)
        if choice_id:
            # Only accept a choice that really belongs to this question
            chosen = next((c for c in question.choices.all() if c.id == choice_id), None)
        correct = bool(chosen and chosen.is_correct)
        score += int(correct)
        answers.append(
            AttemptAnswer(attempt=attempt, question=question, choice=chosen, is_correct=correct)
        )

    with transaction.atomic():
        AttemptAnswer.objects.bulk_create(answers)
        attempt.score = score
        attempt.total = len(answers)
        attempt.finished_at = timezone.now()
        attempt.save()


@login_required
def quiz_start(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    if request.method != "POST":
        return redirect("quiz_detail", pk=pk)
    if not quiz.questions.exists():
        messages.error(request, "This quiz has no questions yet.")
        return redirect("quiz_list")

    # Resume a running attempt instead of starting a second one
    attempt = Attempt.objects.filter(
        user=request.user, quiz=quiz, finished_at__isnull=True
    ).first()
    if attempt and attempt.seconds_left <= -GRACE_SECONDS:
        grade_attempt(attempt, {})  # old attempt ran out of time
        attempt = None
    if attempt is None:
        attempt = Attempt.objects.create(user=request.user, quiz=quiz)
    return redirect("attempt_take", pk=attempt.pk)


@login_required
def attempt_take(request, pk):
    # user=request.user -> nobody can open someone else's attempt
    attempt = get_object_or_404(Attempt, pk=pk, user=request.user)
    if attempt.finished_at:
        return redirect("attempt_result", pk=pk)

    if request.method == "POST":
        if attempt.seconds_left < -GRACE_SECONDS:
            # Submitted far too late: the server does not trust the browser timer
            selected = {}
            messages.warning(request, "Time was over, so your answers were not counted.")
        else:
            selected = {}
            for key, value in request.POST.items():
                if key.startswith("q_") and key[2:].isdigit() and value.isdigit():
                    selected[int(key[2:])] = int(value)
        grade_attempt(attempt, selected)
        return redirect("attempt_result", pk=pk)

    if attempt.seconds_left <= 0:
        grade_attempt(attempt, {})
        messages.warning(request, "Time was over.")
        return redirect("attempt_result", pk=pk)

    context = {
        "attempt": attempt,
        "quiz": attempt.quiz,
        "questions": attempt.quiz.questions.prefetch_related("choices"),
        "seconds_left": int(attempt.seconds_left),
    }
    return render(request, "quiz/attempt_take.html", context)


@login_required
def attempt_result(request, pk):
    attempt = get_object_or_404(Attempt, pk=pk, user=request.user)
    if not attempt.finished_at:
        return redirect("attempt_take", pk=pk)

    answers = (
        attempt.answers.select_related("question", "choice")
        .prefetch_related("question__choices")
        .order_by("question__order", "question__id")
    )
    review = []
    for answer in answers:
        correct = next((c for c in answer.question.choices.all() if c.is_correct), None)
        review.append({"answer": answer, "correct": correct})

    return render(request, "quiz/attempt_result.html", {"attempt": attempt, "review": review})

@login_required
def practice_mode(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)

    questions = quiz.questions.prefetch_related("choices")

    context = {
        "quiz": quiz,
        "questions": questions,
    }

    return render(request, "quiz/practice_mode.html", context)

@login_required
def my_attempts(request):
    attempts = (
        Attempt.objects.filter(user=request.user, finished_at__isnull=False)
        .select_related("quiz")
    )
    return render(request, "quiz/my_attempts.html", {"attempts": attempts})


def leaderboard(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)
    # One row per user with their best score (SQL GROUP BY)
    rows = (
        Attempt.objects.filter(quiz=quiz, finished_at__isnull=False)
        .values("user__username")
        .annotate(best=Max("score"), tries=Count("id"))
        .order_by("-best", "user__username")[:10]
    )
    context = {"quiz": quiz, "rows": rows, "num_questions": quiz.questions.count()}
    return render(request, "quiz/leaderboard.html", context)
