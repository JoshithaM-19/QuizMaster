from datetime import timedelta

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Quiz(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="quizzes")
    time_limit_minutes = models.PositiveIntegerField(
        default=5, validators=[MinValueValidator(1)]
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "quizzes"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=300)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class Attempt(models.Model):
    """One try of a quiz by one user. finished_at is empty while the quiz is running."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attempts")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="attempts")
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.user} - {self.quiz} ({self.score}/{self.total})"

    @property
    def deadline(self):
        return self.started_at + timedelta(minutes=self.quiz.time_limit_minutes)

    @property
    def seconds_left(self):
        """Time remaining, calculated on the server (so refreshing the page cannot reset the timer)."""
        return (self.deadline - timezone.now()).total_seconds()

    @property
    def percent(self):
        return round(self.score * 100 / self.total) if self.total else 0
        
    @property
    def time_taken(self):
        """Return the time spent on the quiz in minutes and seconds."""
        if not self.finished_at:
            return None

        total_seconds = max(
            0, int((self.finished_at - self.started_at).total_seconds())
        )

        minutes = total_seconds // 60
        seconds = total_seconds % 60

        if minutes:
            return f"{minutes} min {seconds} sec"
        return f"{seconds} sec"


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True, blank=True)
    is_correct = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="one_answer_per_question")
        ]
