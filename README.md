# QuizMaster - Online Quiz Platform (Django)

Users register, take timed quizzes, see detailed answer reviews and compete on a leaderboard. Admins create quizzes from the Django admin panel.

**Tech:** Python, Django, SQLite, HTML, CSS, JavaScript

## Features
- Register / login / logout (Django auth)
- Browse, search and filter quizzes by category
- Timed quiz with a JavaScript countdown that auto-submits at 00:00
- Server-side time check (the timer cannot be cheated by editing JS)
- Automatic scoring and a review page showing correct vs your answers
- Per-quiz leaderboard (best score per user) and "My results" history
- Admin panel to add quizzes, questions and choices

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt

python manage.py makemigrations quiz
python manage.py migrate
python manage.py seed_demo         # adds 2 sample quizzes
python manage.py createsuperuser   # for /admin/ (to add your own quizzes)
python manage.py runserver
```

Open http://127.0.0.1:8000/ and register an account.

## Project structure

| File | What it does |
|------|--------------|
| `quizmaster/settings.py` | Settings: apps, database, templates, static files, login URLs |
| `quizmaster/urls.py` | Root URLs, hands everything to the `quiz` app |
| `quiz/models.py` | Category, Quiz, Question, Choice, Attempt, AttemptAnswer |
| `quiz/views.py` | All logic: list/search, start quiz, take quiz, grading, result, leaderboard |
| `quiz/urls.py` | URL to view mapping |
| `quiz/admin.py` | Admin screens with inline editing of questions and choices |
| `quiz/management/commands/seed_demo.py` | Custom command that creates demo quizzes |
| `templates/` | HTML pages (`base.html` is the shared layout) |
| `static/css/style.css` | Styling (responsive) |
| `static/js/main.js` | Countdown timer, auto-submit, answered counter |

## Database design

```
Category 1---* Quiz 1---* Question 1---* Choice (is_correct)
User 1---* Attempt *---1 Quiz
Attempt 1---* AttemptAnswer *---1 Question   (and a chosen Choice)
```

## How a quiz attempt works

1. User clicks **Start** (a POST) and an `Attempt` is created with `started_at`.
2. The server calculates `seconds_left = deadline - now` and sends it to the page.
3. JS counts down from that number. At 0 it submits the form automatically.
4. On submit, `grade_attempt()` compares each chosen choice with `is_correct`, saves `AttemptAnswer` rows and the final score.
5. If the answers arrive more than 15 seconds after the deadline, the server ignores them. The browser is never trusted.

## Interview Q&A

**Explain your project in 30 seconds.**
QuizMaster is a Django app where users take timed quizzes. It has authentication, a JavaScript countdown timer, automatic scoring, a review page and a leaderboard. Admins manage quizzes from the Django admin.

**How did you build the timer?**
The server stores `started_at` and calculates the remaining seconds. JavaScript uses `setInterval` to count down and auto-submit the form at zero. Because the time comes from the server, refreshing the page does not reset it.

**Can a user cheat by changing the JavaScript timer?**
No. The server checks the time again on submit. If the submission is later than the deadline plus a 15-second grace period, the answers are ignored.

**How is the score calculated?**
`grade_attempt()` loops over the questions. For each one it finds the choice the user selected, checks that it belongs to that question and has `is_correct=True`, and adds 1. Everything is saved inside `transaction.atomic()`.

**Why is the selected choice checked against the question?**
A user could send a fake choice ID in the form. Looking the choice up in `question.choices` means only valid choices for that question are accepted.

**How is the leaderboard built?**
`Attempt.objects.values("user__username").annotate(best=Max("score"), tries=Count("id"))` which is a SQL GROUP BY. It gives one row per user with their best score.

**How do you stop users opening each other's results?**
`get_object_or_404(Attempt, pk=pk, user=request.user)` returns a 404 for attempts that belong to someone else.

**What is the relationship between your models?**
One-to-many chains: Category to Quiz to Question to Choice. Attempt links a User to a Quiz, and AttemptAnswer stores each answer. `UniqueConstraint` ensures one answer per question per attempt.

**What is `select_related` / `prefetch_related`?**
Both reduce database queries. `select_related` uses a SQL JOIN for foreign keys. `prefetch_related` runs one extra query for reverse/many relations (like a question's choices) and joins them in Python. They avoid the N+1 query problem.

**Why POST for starting a quiz?**
It creates data (an Attempt), and GET requests should be safe. It also stops a link or image from starting quizzes accidentally. Forms include `{% csrf_token %}` for protection.

**What would you add next?**
Multiple-answer questions, random question order, quiz categories with difficulty, email results, a REST API, and unit tests.

## Practice ideas
1. Shuffle the order of questions and choices.
2. Add a `difficulty` field to Quiz and filter by it.
3. Show the time taken on the leaderboard and use it to break ties.
4. Write tests for `grade_attempt()` in `quiz/tests.py`.
