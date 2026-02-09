from rest_framework import viewsets, permissions
from .models import TrainingSession
from .serializers import TrainingSessionSerializer


class TrainingSessionViewSet(viewsets.ModelViewSet):
    """Работа с сессиями"""
    serializer_class = TrainingSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Каждый видит только свои сессии
        return TrainingSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Автоматически привязываем пользователя
        serializer.save(user=self.request.user)

    # PUT, PATCH отключаем пока
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
