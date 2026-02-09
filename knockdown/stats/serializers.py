from rest_framework import serializers
from .models import TrainingSession
from lessons.models import UserLessonProgress


class TrainingSessionSerializer(serializers.ModelSerializer):
    """Сохраняет сессию и автоматически обновляет прогресс"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = TrainingSession
        fields = [
            'id', 'user', 'lesson', 'lesson_title',
            'average_speed_wpm', 'accuracy_percentage',
            'total_duration_seconds', 'total_characters_typed', 'total_errors',
            'started_at', 'finished_at', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'lesson_title']

    def create(self, validated_data):
        # 1. Сохраняем сессию
        session = super().create(validated_data)

        # 2. Обновляем прогресс прямо здесь
        if session.lesson:
            self.update_lesson_progress(session)

        return session

    def update_lesson_progress(self, session):
        """Вся логика прямо здесь"""

        progress, created = UserLessonProgress.objects.get_or_create(
            user=session.user,
            lesson=session.lesson,
            defaults={
                'best_speed': session.average_speed_wpm,
                'best_accuracy': session.accuracy_percentage,
                'completion_count': 1,
                'last_completed_at': session.finished_at
            }
        )

        if not created:
            if session.average_speed_wpm > progress.best_speed:
                progress.best_speed = session.average_speed_wpm

            if session.accuracy_percentage > progress.best_accuracy:
                progress.best_accuracy = session.accuracy_percentage

            progress.completion_count += 1
            progress.last_completed_at = session.finished_at

        # Проверяем прохождение
        if (session.average_speed_wpm >= session.lesson.required_speed and
           session.accuracy_percentage >= session.lesson.required_accuracy and
           not progress.is_passed):
            progress.is_passed = True
            progress.passed_at = session.finished_at

        progress.save()
