from rest_framework import viewsets, permissions
from .models import (
    TrainingSession,
    DailyStatistics,
    DailyLetterStatistics,
    DailyBigramStatistics
)
from .serializers import (
    TrainingSessionSerializer,
    DashboardStatsSerializer,
    DailyStatisticsSerializer,
    ProblemLetterSerializer,
    ProblemBigramSerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Max


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


class DashboardStatsView(APIView):
    """Общая статистика пользователя для профиля"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        stats = TrainingSession.objects.filter(user=user).aggregate(
            total_sessions=Count('id'),
            total_time=Sum('total_duration_seconds'),
            avg_speed=Avg('average_speed_wpm'),
            best_speed=Max('average_speed_wpm'),
            avg_accuracy=Avg('accuracy_percentage')
        )

        data = {
            'total_sessions': stats['total_sessions'] or 0,
            'total_time': round((stats['total_time'] or 0) / 60),
            'avg_speed': round(stats['avg_speed'] or 0),
            'best_speed': stats['best_speed'] or 0,
            'avg_accuracy': round(stats['avg_accuracy'] or 0),
        }

        serializer = DashboardStatsSerializer(data)
        return Response(serializer.data)

        # return Response({
        #     'total_sessions': stats['total_sessions'] or 0,
        #     'total_time': round((stats['total_time'] or 0) / 60),  # в мин
        #     'avg_speed': round(stats['avg_speed'] or 0),
        #     'best_speed': stats['best_speed'] or 0,
        #     'avg_accuracy': round(stats['avg_accuracy'] or 0),
        # })


class DailyStatsView(APIView):
    """Дневная статистика для графика"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        daily_stats = DailyStatistics.objects.filter(
            user=user
        ).order_by('-date')[:30]
        serializer = DailyStatisticsSerializer(daily_stats, many=True)
        return Response(serializer.data)


class LetterStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        stats = DailyLetterStatistics.objects.filter(user=user)

        aggregated = {}
        for stat in stats:
            if stat.letter not in aggregated:
                aggregated[stat.letter] = {
                    'occurrences': 0,
                    'errors': 0,
                    'total_time': 0,
                    'count': 0
                }
            aggregated[stat.letter]['occurrences'] += stat.total_occurrences
            aggregated[stat.letter]['errors'] += stat.total_errors
            if stat.average_hit_time_ms:
                aggregated[stat.letter]['total_time'] += (
                    stat.average_hit_time_ms * stat.total_occurrences
                )
                aggregated[stat.letter]['count'] += stat.total_occurrences

        result = []
        for letter, data in aggregated.items():
            if data['occurrences'] > 5:
                result.append({
                    'letter': letter,
                    'occurrences': data['occurrences'],
                    'errors': data['errors'],
                    'error_percent': round(
                        data['errors'] / data['occurrences'] * 100, 1
                    ),
                    'avg_time': round(
                        data['total_time'] / data['count'], 1
                    ) if data['count'] > 0 else 0
                })

        # Сортировка: сначала по проценту ошибок (от большего к меньшему), затем по времени перехода (от большего к меньшему)
        result.sort(key=lambda x: (-x['error_percent'], -x['avg_time']))

        serializer = ProblemLetterSerializer(result[:15], many=True)
        return Response(serializer.data)


class BigramStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        stats = DailyBigramStatistics.objects.filter(user=user)

        aggregated = {}
        for stat in stats:
            if stat.bigram not in aggregated:
                aggregated[stat.bigram] = {
                    'occurrences': 0,
                    'errors': 0,
                    'total_time': 0,
                    'count': 0
                }
            aggregated[stat.bigram]['occurrences'] += stat.total_occurrences
            aggregated[stat.bigram]['errors'] += stat.total_errors
            if stat.average_transition_time_ms:
                aggregated[stat.bigram]['total_time'] += (
                    stat.average_transition_time_ms * stat.total_occurrences
                )
                aggregated[stat.bigram]['count'] += stat.total_occurrences

        result = []
        for bigram, data in aggregated.items():
            if data['occurrences'] > 3:
                result.append({
                    'bigram': bigram,
                    'occurrences': data['occurrences'],
                    'errors': data['errors'],
                    'error_percent': round(
                        data['errors'] / data['occurrences'] * 100, 1
                    ),
                    'avg_time': round(
                        data['total_time'] / data['count'], 1
                    ) if data['count'] > 0 else 0
                })

        result.sort(key=lambda x: x['error_percent'], reverse=True)

        serializer = ProblemBigramSerializer(result[:15], many=True)
        return Response(serializer.data)
