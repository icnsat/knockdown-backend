from rest_framework import viewsets
from stats.models import TrainingSession
'''
from stats.serializers import TrainingSessionSerializer

class TrainingSessionViewSet(viewsets.ModelViewSet):
    serializer_class = TrainingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrainingSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        session = serializer.save(user=self.request.user)

        # Автоматически обновляем прогресс урока
        if session.lesson:
            self.update_lesson_progress(session)

    def update_lesson_progress(self, session):
        """Вызывает обновление прогресса через сериализатор"""
        from lessons.serializers import LessonProgressUpdateSerializer

        progress_data = {
            'lesson_id': session.lesson.id,
            'speed': session.average_speed_wpm,
            'accuracy': session.accuracy_percentage
        }

        progress_serializer = LessonProgressUpdateSerializer(data=progress_data)
        if progress_serializer.is_valid():
            progress_serializer.update_progress(session.user)
'''
