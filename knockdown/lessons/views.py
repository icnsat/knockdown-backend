from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Lesson, UserLessonProgress
from .serializers import (
    LessonSerializer,
    LessonDetailSerializer,
    LessonListSerializer,
    UserLessonProgressSerializer,
    LessonProgressUpdateSerializer,
    # GeneratedLessonSerializer
)
# from .services import LessonGenerator


class LessonViewSet(viewsets.ModelViewSet):
    """Работа чисто с уроками"""
    queryset = Lesson.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        elif self.action == 'retrieve':
            return LessonDetailSerializer
        return LessonSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class UserLessonProgressViewSet(viewsets.ModelViewSet):
    """Работа с прогрессом"""
    serializer_class = UserLessonProgressSerializer  # Обычный сериализатор для ручной работы
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserLessonProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def update_after_session(self, request):
        """Автообновление прогресса после тренировочной сессии"""
        serializer = LessonProgressUpdateSerializer(data=request.data)
        if serializer.is_valid():
            progress = serializer.update_progress(request.user)
            return Response(
                UserLessonProgressSerializer(progress).data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
class GenerateLessonView(APIView):
    """Генерация уроков"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Генерация персонализированного урока
        Параметры: type, difficulty, target_letters, target_bigrams
        """
        generator = LessonGenerator(request.user)

        # Получаем параметры или используем статистику пользователя
        lesson_type = request.data.get('type', 'auto')  # auto - определит сам
        difficulty = request.data.get('difficulty')
        target_letters = request.data.get('target_letters')
        target_bigrams = request.data.get('target_bigrams')

        # Генерация урока
        lesson_data = generator.generate(
            lesson_type=lesson_type,
            difficulty=difficulty,
            target_letters=target_letters,
            target_bigrams=target_bigrams
        )

        # Сериализация ответа
        serializer = GeneratedLessonSerializer(data=lesson_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
'''

# Доп. функционал
'''
class RecommendedLessonsView(APIView):
    """Для рекомендации существующих уроков по проблемам"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. Следующий урок в курсе
        next_lesson = self.get_next_in_course(user)

        # 2. Уроки для проблемных зон
        problem_lessons = self.get_problem_area_lessons(user)

        # 3. Случайный подходящий урок
        random_lesson = self.get_random_suitable_lesson(user)

        response_data = {
            'next_in_course': LessonListSerializer(next_lesson).data if next_lesson else None,
            'for_problem_areas': LessonListSerializer(problem_lessons, many=True).data,
            'random_suitable': LessonListSerializer(random_lesson).data if random_lesson else None
        }

        return Response(response_data)

    def get_next_in_course(self, user):
        """Следующий непройденный урок по order_index"""
        # Находим последний пройденный урок
        last_passed = UserLessonProgress.objects.filter(
            user=user, is_passed=True
        ).order_by('lesson__order_index').last()

        if last_passed:
            next_order = last_passed.lesson.order_index + 1
        else:
            next_order = 1

        return Lesson.objects.filter(order_index=next_order).first()
'''
