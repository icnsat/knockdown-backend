from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from lessons.models import Lesson
from stats.models import TrainingSession, LetterStatistics, BigramStatistics

User = get_user_model()


class TrainingSessionModelTest(TestCase):
    """Модульные тесты для моделей статистики"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='test content',
            required_speed=100,
            required_accuracy=95
        )

    def test_create_training_session(self):
        """Тест создания тренировочной сессии"""
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

        self.assertEqual(session.user.username, 'testuser')
        self.assertEqual(session.average_speed_wpm, 120)
        self.assertEqual(session.accuracy_percentage, 95)
        self.assertEqual(session.total_errors, 5)

    def test_session_str_method(self):
        """Тест строкового представления сессии"""
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
        self.assertEqual(str(session), self.user.username)

    def test_letter_statistics_creation(self):
        """Тест создания статистики по буквам"""
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

        letter_stat = LetterStatistics.objects.create(
            session=session,
            user=self.user,
            letter='а',
            occurrences=15,
            errors=2,
            average_hit_time_ms=120
        )

        self.assertEqual(letter_stat.letter, 'а')
        self.assertEqual(letter_stat.occurrences, 15)
        self.assertEqual(letter_stat.errors, 2)
        self.assertEqual(letter_stat.average_hit_time_ms, 120)

    def test_bigram_statistics_creation(self):
        """Тест создания статистики по биграммам"""
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

        bigram_stat = BigramStatistics.objects.create(
            session=session,
            user=self.user,
            bigram='ст',
            occurrences=5,
            errors=1,
            average_transition_time_ms=130
        )

        self.assertEqual(bigram_stat.bigram, 'ст')
        self.assertEqual(bigram_stat.occurrences, 5)
        self.assertEqual(bigram_stat.errors, 1)
        self.assertEqual(bigram_stat.average_transition_time_ms, 130)