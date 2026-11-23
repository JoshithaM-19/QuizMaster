from django.core.management.base import BaseCommand

from quiz.models import Category, Choice, Question, Quiz

# Each question: (text, [choices], index of the correct choice)
DEMO = {
    "Python Basics": {
        "category": "Python",
        "description": "Five quick questions on core Python.",
        "questions": [
            ("Which keyword defines a function in Python?", ["def", "func", "function", "define"], 0),
            ("Which of these is immutable?", ["list", "dict", "tuple", "set"], 2),
            ("What does len('hello') return?", ["4", "5", "6", "Error"], 1),
            ("Which symbol starts a single-line comment?", ["//", "#", "--", "/*"], 1),
            ("What is the type of [1, 2, 3]?", ["tuple", "set", "dict", "list"], 3),
        ],
    },
    "Django Basics": {
        "category": "Django",
        "description": "Test what you know about Django.",
        "questions": [
            ("Which pattern does Django follow?", ["MVT", "MVVM", "MVP", "Singleton"], 0),
            ("Which command starts the development server?",
             ["python manage.py serve", "python manage.py runserver", "python manage.py start", "django run"], 1),
            ("Which file maps URLs to views?", ["models.py", "views.py", "urls.py", "admin.py"], 2),
            ("Which command applies migrations to the database?",
             ["makemigrations", "migrate", "runmigrations", "dbsync"], 1),
            ("Which template tag protects a POST form from CSRF?",
             ["{% secure %}", "{% token %}", "{% protect %}", "{% csrf_token %}"], 3),
        ],
    },
        
    "SQL & Database": {
        "category": "SQL",
        "description": "Practice questions on SQL and database fundamentals.",
        "questions": [
            ("Which SQL command is used to retrieve data from a table?",
             ["GET", "SELECT", "FETCH", "READ"], 1),
            ("Which command is used to add a new row to a table?",
             ["INSERT", "ADD", "CREATE", "APPEND"], 0),
            ("Which SQL command is used to modify existing data?",
             ["CHANGE", "UPDATE", "MODIFY", "ALTER"], 1),
            ("Which clause is used to filter rows in a SELECT query?",
             ["ORDER BY", "GROUP BY", "WHERE", "HAVING"], 2),
            ("Which key uniquely identifies each row in a table?",
             ["Foreign key", "Primary key", "Candidate key", "Index"], 1),
            ("Which SQL command removes a table completely?",
             ["DELETE", "REMOVE", "DROP", "CLEAR"], 2),
            ("Which function returns the number of rows?",
             ["SUM()", "COUNT()", "TOTAL()", "NUMBER()"], 1),
            ("Which JOIN returns matching rows from both tables?",
             ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"], 0),
            ("Which constraint prevents duplicate values in a column?",
             ["UNIQUE", "CHECK", "DEFAULT", "NOT NULL"], 0),
            ("Which SQL command is used to sort query results?",
             ["SORT BY", "ORDER BY", "GROUP BY", "ARRANGE BY"], 1),
        ],
    },
        "Python OOP": {
        "category": "Python",
        "description": "Practice questions on object-oriented programming in Python.",
        "questions": [
            ("Which keyword is used to define a class in Python?",
             ["class", "object", "struct", "define"], 0),
            ("What is an object?",
             ["A function", "An instance of a class", "A module", "A variable type"], 1),
            ("Which method is commonly used as a constructor in Python?",
             ["__start__", "__create__", "__init__", "__newclass__"], 2),
            ("What does inheritance allow a class to do?",
             ["Delete another class", "Reuse properties and methods of another class",
              "Create only variables", "Prevent object creation"], 1),
            ("Which concept hides internal implementation details?",
             ["Inheritance", "Polymorphism", "Encapsulation", "Iteration"], 2),
            ("What does polymorphism allow?",
             ["Different objects to respond to the same method in different ways",
              "Only one object to exist", "A class to have no methods", "Variables to become constants"], 0),
            ("Which keyword refers to the current object inside an instance method?",
             ["this", "self", "current", "object"], 1),
            ("Which symbol is used to access an object's attribute or method?",
             ["->", "::", ".", "#"], 2),
            ("Can a Python class contain both variables and methods?",
             ["Yes", "No", "Only variables", "Only methods"], 0),
            ("What is method overriding?",
             ["Deleting a method",
              "Defining a subclass method with the same name as a parent class method",
              "Calling a method twice",
              "Creating a method outside a class"], 1),
        ],
    },
}




class Command(BaseCommand):
    help = "Create four demo quizzes so you can try the app immediately."

    def handle(self, *args, **options):
        for title, data in DEMO.items():
            category, _ = Category.objects.get_or_create(name=data["category"])
            quiz, created = Quiz.objects.get_or_create(
                title=title,
                defaults={
                    "category": category,
                    "description": data["description"],
                    "time_limit_minutes": 5,
                },
            )
            if not created:
                self.stdout.write(f"'{title}' already exists, skipped.")
                continue
            for order, (text, choices, correct_index) in enumerate(data["questions"], start=1):
                question = Question.objects.create(quiz=quiz, text=text, order=order)
                for i, choice_text in enumerate(choices):
                    Choice.objects.create(
                        question=question, text=choice_text, is_correct=(i == correct_index)
                    )
            self.stdout.write(self.style.SUCCESS(f"Created quiz '{title}'."))
