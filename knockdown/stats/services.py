from django.db.models import Sum, Avg
from .models import (
    TrainingSession,
    DailyStatistics,
    DailyLetterStatistics,
    DailyBigramStatistics,
    LetterStatistics,
    BigramStatistics
)


class DailyStatsService:
    """Обновляет агрегированную статистику за день"""

    @staticmethod
    def update_all(session):
        """Обновление всех видов дневной статистики после сессии"""
        date = session.finished_at.date()

        DailyStatsService.update_general_stats(session.user, date, session)
        DailyStatsService.update_letter_stats(session.user, date)
        DailyStatsService.update_bigram_stats(session.user, date)

    @staticmethod
    def update_general_stats(user, date, session):
        """Обновление общей дневной статистики"""
        daily, _ = DailyStatistics.objects.get_or_create(
            user=user,
            date=date,
            defaults={
                'total_training_time_seconds': 0,
                'total_sessions': 0,
                'best_speed_wpm': 0,
                'average_speed_wpm': 0,
                'average_accuracy_percentage': 0
            }
        )

        # Получаем все сессии за день (включая новую)
        sessions = TrainingSession.objects.filter(
            user=user,
            finished_at__date=date
        )

        # Пересчитываем агрегаты
        total_time = sum(s.total_duration_seconds for s in sessions)
        total_sessions = sessions.count()
        best_speed = max(s.average_speed_wpm for s in sessions)
        avg_speed = sum(s.average_speed_wpm for s in sessions) / total_sessions
        avg_accuracy = sum(
            s.accuracy_percentage for s in sessions
        ) / total_sessions

        # Обновляем запись
        daily.total_training_time_seconds = total_time
        daily.total_sessions = total_sessions
        daily.best_speed_wpm = best_speed
        daily.average_speed_wpm = avg_speed
        daily.average_accuracy_percentage = avg_accuracy
        daily.save()

    @staticmethod
    def update_letter_stats(user, date):
        """Обновление дневной статистики по буквам"""
        # Получаем все статистики по буквам за день
        letter_stats = LetterStatistics.objects.filter(
            user=user,
            session__finished_at__date=date
        )

        # Группируем по буквам
        aggregated = letter_stats.values('letter').annotate(
            total_occurrences=Sum('occurrences'),
            total_errors=Sum('errors'),
            avg_time=Avg('average_hit_time_ms')
        )

        # Сохраняем или обновляем дневные записи
        for stat in aggregated:
            DailyLetterStatistics.objects.update_or_create(
                user=user,
                date=date,
                letter=stat['letter'],
                defaults={
                    'total_occurrences': stat['total_occurrences'],
                    'total_errors': stat['total_errors'],
                    'average_hit_time_ms': stat['avg_time'] or 0
                }
            )

    @staticmethod
    def update_bigram_stats(user, date):
        """Обновление дневной статистики по биграммам"""
        bigram_stats = BigramStatistics.objects.filter(
            user=user,
            session__finished_at__date=date
        )

        aggregated = bigram_stats.values('bigram').annotate(
            total_occurrences=Sum('occurrences'),
            total_errors=Sum('errors'),
            avg_time=Avg('average_transition_time_ms')
        )

        for stat in aggregated:
            DailyBigramStatistics.objects.update_or_create(
                user=user,
                date=date,
                bigram=stat['bigram'],
                defaults={
                    'total_occurrences': stat['total_occurrences'],
                    'total_errors': stat['total_errors'],
                    'average_transition_time_ms': stat['avg_time'] or 0
                }
            )
