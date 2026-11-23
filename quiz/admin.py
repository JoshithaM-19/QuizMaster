from django.contrib import admin

from .models import Attempt, Category, Choice, Question, Quiz


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 3


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "time_limit_minutes", "is_published")
    list_filter = ("category", "is_published")
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "quiz", "order")
    list_filter = ("quiz",)
    inlines = [ChoiceInline]


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "total", "finished_at")
    list_filter = ("quiz",)
