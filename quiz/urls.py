from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("quiz/<int:pk>/", views.quiz_detail, name="quiz_detail"),
    path("quiz/<int:pk>/start/", views.quiz_start, name="quiz_start"),
    path("quiz/<int:pk>/practice/", views.practice_mode, name="practice_mode"),
    path("quiz/<int:pk>/leaderboard/", views.leaderboard, name="leaderboard"),
    path("attempt/<int:pk>/", views.attempt_take, name="attempt_take"),
    path("attempt/<int:pk>/result/", views.attempt_result, name="attempt_result"),
    path("my-attempts/", views.my_attempts, name="my_attempts"),
    path("register/", views.register, name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
