from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from lessons.models import Lesson, UserLessonProgress
from stats.models import TrainingSession

User = get_user_model()


class TrainingSessionAPITest(APITestCase):
    """Интеграционные тесты для API тренировочных сессий"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.lesson = Lesson.objects.create(
            title='Базовый урок',
            content='текст для тренировки',
            required_speed=100,
            required_accuracy=90,
            difficulty_level=1,
            lesson_type='basic'
        )
        self.url = reverse('session-list')

    def test_get_sessions_unauthorized(self):
        """
        Тест: получение списка сессий без авторизации
        Ожидается: статус 401 Unauthorized
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_sessions_authorized(self):
        """
        Тест: получение списка сессий авторизованным пользователем
        Ожидается: статус 200 OK, список сессий
        """
        self.client.force_authenticate(user=self.user)

        TrainingSession.objects.create(
            user=self.user,
            lesson=self.lesson,
            total_duration_seconds=60,
            total_characters_typed=100,
            total_errors=5,
            average_speed_wpm=120,
            accuracy_percentage=95,
            started_at=timezone.now(),
            finished_at=timezone.now()
        )

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_session_authorized(self):
        """
        Тест: создание сессии авторизованным пользователем
        Ожидается: статус 201 Created, сессия сохранена в БД
        """
        self.client.force_authenticate(user=self.user)

        data = {
            'lesson': self.lesson.id,
            'total_duration_seconds': 60,
            'total_characters_typed': 100,
            'total_errors': 5,
            'average_speed_wpm': 120,
            'accuracy_percentage': 95,
            'started_at': '2024-01-01T10:00:00Z',
            'finished_at': '2024-01-01T10:01:00Z'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrainingSession.objects.count(), 1)

    def test_create_session_without_auth(self):
        """
        Тест: создание сессии без авторизации
        Ожидается: статус 401 Unauthorized
        """
        data = {
            'lesson': self.lesson.id,
            'total_duration_seconds': 60,
            'total_characters_typed': 100,
            'total_errors': 5,
            'average_speed_wpm': 120,
            'accuracy_percentage': 95,
            'started_at': '2024-01-01T10:00:00Z',
            'finished_at': '2024-01-01T10:01:00Z'
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_session_authorized(self):
        """
        Тест: удаление сессии авторизованным пользователем
        Ожидается: статус 204 No Content, сессия удалена из БД
        """
        self.client.force_authenticate(user=self.user)

        session = TrainingSession.objects.create(
            user=self.user,
            lesson=self.lesson,
            total_duration_seconds=60,
            total_characters_typed=100,
            total_errors=5,
            average_speed_wpm=120,
            accuracy_percentage=95,
            started_at=timezone.now(),
            finished_at=timezone.now()
        )

        url = reverse('session-detail', args=[session.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TrainingSession.objects.count(), 0)

    def test_progress_created_after_first_session(self):
        """
        Тест: проверка обновления прогресса
        после сохранения тренировочной сессии
        Ожидается: создаётся запись прогресса с правильными значениями
        """
        self.client.force_authenticate(user=self.user)

        session_data = {
            'lesson': self.lesson.id,
            'total_duration_seconds': 60,
            'total_characters_typed': 100,
            'total_errors': 5,
            'average_speed_wpm': 120,
            'accuracy_percentage': 95,
            'started_at': '2024-01-01T10:00:00Z',
            'finished_at': '2024-01-01T10:01:00Z'
        }

        response = self.client.post(self.url, session_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        progress = UserLessonProgress.objects.get(
            user=self.user,
            lesson=self.lesson
        )

        self.assertEqual(progress.best_speed, 120)
        self.assertEqual(progress.best_accuracy, 95)
        self.assertEqual(progress.completion_count, 1)

        self.assertTrue(progress.is_passed)
