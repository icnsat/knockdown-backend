from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from lessons.models import Lesson
from stats.serializers import TrainingSessionSerializer

User = get_user_model()


class TrainingSessionSerializerTest(TestCase):
    """Модульные тесты для сериализатора тренировочных сессий"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='test content',
            required_speed=100,
            required_accuracy=95
        )

    def test_valid_serializer_data(self):
        """Тест валидных данных сериализатора"""
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

        serializer = TrainingSessionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_accuracy(self):
        """Тест невалидной точности (больше 100%)"""
        data = {
            'lesson': self.lesson.id,
            'total_duration_seconds': 60,
            'total_characters_typed': 100,
            'total_errors': 5,
            'average_speed_wpm': 120,
            'accuracy_percentage': 150,
            'started_at': '2024-01-01T10:00:00Z',
            'finished_at': '2024-01-01T10:01:00Z'
        }

        serializer = TrainingSessionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('accuracy_percentage', serializer.errors)

    def test_negative_speed(self):
        """Тест отрицательной скорости"""
        data = {
            'lesson': self.lesson.id,
            'total_duration_seconds': 60,
            'total_characters_typed': 100,
            'total_errors': 5,
            'average_speed_wpm': -10,
            'accuracy_percentage': 95,
            'started_at': '2024-01-01T10:00:00Z',
            'finished_at': '2024-01-01T10:01:00Z'
        }

        serializer = TrainingSessionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('average_speed_wpm', serializer.errors)

    def test_finished_at_before_started_at(self):
        """Тест: время окончания раньше времени начала"""
        data = {
            'lesson': self.lesson.id,
            'total_duration_seconds': 60,
            'total_characters_typed': 100,
            'total_errors': 5,
            'average_speed_wpm': 120,
            'accuracy_percentage': 95,
            'started_at': '2024-01-01T10:01:00Z',
            'finished_at': '2024-01-01T10:00:00Z'
        }

        serializer = TrainingSessionSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('finished_at', serializer.errors)