from django.db import models


class TrainingSession(models.Model):
    # EXERCISE_TYPES = [
    #     ('lesson', 'Урок'),
    #     ('words', 'Слова'),
    #     ('text', 'Текст'),
    #     ('free', 'Свободный набор'),
    # ]

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    lesson = models.ForeignKey(
        'lessons.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    # exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPES)
    # lesson_title = models.CharField(max_length=255, blank=True)

    # Статистика
    total_duration_seconds = models.IntegerField()
    total_characters_typed = models.IntegerField()
    total_errors = models.IntegerField()
    average_speed_wpm = models.FloatField()  # знаков в минуту
    accuracy_percentage = models.FloatField()

    # Мета
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-finished_at']

    def __str__(self):
        if self.lesson:
            info = (
                f"{self.lesson.order_index}. "
                f"{self.lesson.title}"
            )
        else:
            info = "Сгенерированный урок"

        return f"{self.user.username}: {info} - {self.average_speed_wpm} wpm"


class DailyStatistics(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateField()
    total_training_time_seconds = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    best_speed_wpm = models.FloatField(default=0)
    average_speed_wpm = models.FloatField(default=0)
    average_accuracy_percentage = models.FloatField(default=0)

    class Meta:
        unique_together = ['user', 'date']
        indexes = [
            models.Index(fields=['user', '-date']),
        ]

    def __str__(self):
        return (
            f"{self.date} - {self.user.username}"
        )


class LetterStatistics(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)  # денормализация
    letter = models.CharField(max_length=3)   # спец клавиши
    occurrences = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    average_hit_time_ms = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'letter']),
        ]

    def __str__(self):
        if self.session and self.session.lesson:
            info = (
                f"{self.session.lesson.order_index}. "
                f"{self.session.lesson.title}"
            )
        else:
            info = "Сгенерированный урок"

        return f"{self.user.username}: {info} - '{self.letter}'"


class DailyLetterStatistics(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateField()
    letter = models.CharField(max_length=3)
    total_occurrences = models.IntegerField(default=0)
    total_errors = models.IntegerField(default=0)
    average_hit_time_ms = models.FloatField()

    class Meta:
        unique_together = ['user', 'date', 'letter']

    def __str__(self):
        return (
            f"{self.date} - {self.user.username}: '{self.letter}'"
        )


class BigramStatistics(models.Model):
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    bigram = models.CharField(
        max_length=6,
    )  # 'ab', 'a\t', '\ls\rs' or '\l\r' - haven't decided yet
    occurrences = models.IntegerField(default=0)
    errors = models.IntegerField(default=0)
    average_transition_time_ms = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'bigram']),
        ]

    def __str__(self):
        # Безопасное получение номера урока и названия
        if self.session and self.session.lesson:
            info = (
                f"{self.session.lesson.order_index}. "
                f"{self.session.lesson.title}"
            )
        else:
            info = "Сгенерированный урок"

        return f"{self.user.username}: {info} - '{self.bigram}'"


class DailyBigramStatistics(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateField()
    bigram = models.CharField(max_length=6)
    total_occurrences = models.IntegerField(default=0)
    total_errors = models.IntegerField(default=0)
    average_transition_time_ms = models.FloatField()

    class Meta:
        unique_together = ['user', 'date', 'bigram']

    def __str__(self):
        return (
            f"{self.date} - {self.user.username}: '{self.bigram}'"
        )
