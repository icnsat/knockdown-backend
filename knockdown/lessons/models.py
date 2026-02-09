from django.db import models


class Lesson(models.Model):
    LESSON_TYPES = [
        ('basic', 'Базовый урок'),
        ('problem_letters', 'Проблемные буквы'),
        ('bigrams', 'Биграммы'),
        ('mixed', 'Смешанный'),
        # ('text', 'Текстовый'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField()
    difficulty_level = models.IntegerField() # change to >0
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES) # delete? generated lessons aren't being saved
    order_index = models.IntegerField(default=0)
    required_speed = models.IntegerField()
    required_accuracy = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return f"{self.order_index}. {self.title}"


# only for existing lessons, not fot generated
class UserLessonProgress(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    best_speed = models.IntegerField(default=0)  # зн/мин
    best_accuracy = models.FloatField(default=0)  # %
    completion_count = models.IntegerField(default=0)
    last_completed_at = models.DateTimeField(null=True, blank=True)
    is_passed = models.BooleanField(default=False)
    passed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['user', 'lesson']
        indexes = [
            models.Index(fields=['user', 'is_passed']),
        ]
        ordering = ['passed_at']

    def __str__(self):
        return f"{self.user.username}: {self.lesson.title}"
