from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    LANGUAGES = [
        ('RUS', 'Русский'),
        ('ENG', 'Английский'),
    ]

    LAYOUTS = [
        ('JCUKEN', 'ЙЦУКЕН'),
        ('QWERTY', 'QWERTY'),
    ]

    theme = models.BooleanField(default=True)  # True=light, False=dark
    language = models.CharField(max_length=3, choices=LANGUAGES, default='RUS')
    keyboard_layout = models.CharField(
        max_length=25,
        choices=LAYOUTS,
        default='JCUKEN'
    )

    def __str__(self):
        return self.username
