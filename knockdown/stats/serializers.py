from rest_framework import serializers
from .models import TrainingSession, LetterStatistics, BigramStatistics
from lessons.serializers import UserLessonProgressSerializer


class LetterStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterStatistics
        fields = ['letter', 'occurrences', 'errors', 'average_hit_time_ms']

    def create(self, validated_data):
        session = self.context['session']
        return LetterStatistics.objects.create(
            session=session,
            user=session.user,
            **validated_data
        )


class BigramStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BigramStatistics
        fields = [
            'bigram', 'occurrences', 'errors',
            'average_transition_time_ms'
        ]

    def create(self, validated_data):
        session = self.context['session']
        return BigramStatistics.objects.create(
            session=session,
            user=session.user,
            **validated_data
        )


class TrainingSessionSerializer(serializers.ModelSerializer):
    """Сохраняет сессию и автоматически обновляет прогресс"""
    # Поля для статистики (write_only - не возвращаем в ответе)
    letter_stats = LetterStatsSerializer(
        many=True,
        write_only=True,
        required=False
    )
    bigram_stats = BigramStatsSerializer(
        many=True,
        write_only=True,
        required=False
    )

    # Поля для отображения
    lesson_title = serializers.CharField(
        source='lesson.title',
        read_only=True
    )
    lesson_order = serializers.IntegerField(
        source='lesson.order_index',
        read_only=True
    )

    class Meta:
        model = TrainingSession
        fields = [
            'id', 'user', 'lesson', 'lesson_title', 'lesson_order',
            'total_duration_seconds', 'total_characters_typed', 'total_errors',
            'average_speed_wpm', 'accuracy_percentage',
            'started_at', 'finished_at', 'created_at',
            'letter_stats', 'bigram_stats'  # только для записи
        ]
        read_only_fields = [
            'id', 'user', 'created_at',
            'lesson_title', 'lesson_order'
        ]

    def validate_accuracy_percentage(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Точность должна быть от 0 до 100%"
            )
        return value

    def validate_average_speed_wpm(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Скорость не может быть отрицательной"
            )
        return value

    def validate(self, data):
        """Дополнительные проверки"""
        # Проверяем что finished_at > started_at
        if data.get('started_at') and data.get('finished_at'):
            if data['finished_at'] <= data['started_at']:
                raise serializers.ValidationError({
                    'finished_at':
                    'Время окончания должно быть позже времени начала'
                })

        # Проверяем что длительность логична
        if (
            data.get('total_duration_seconds')
            and data.get('started_at')
            and data.get('finished_at')
        ):
            duration = (
                data['finished_at'] - data['started_at']
            ).total_seconds()
            if abs(duration - data['total_duration_seconds']) > 5:  # допуск
                raise serializers.ValidationError({
                    'total_duration_seconds':
                    'Длительность не соответствует времени начала/окончания'
                })

        return data

    def create(self, validated_data):
        # Извлекаем статистику
        letter_stats_data = validated_data.pop('letter_stats', [])
        bigram_stats_data = validated_data.pop('bigram_stats', [])

        # 1. Сохраняем сессию
        session = super().create(validated_data)

        # 2. Обновляем прогресс урока
        if session.lesson:
            UserLessonProgressSerializer().update_from_session(session)

        # 3. Сохраняем статистику букв
        for data in letter_stats_data:
            letter_serializer = LetterStatsSerializer(
                data=data,
                context={'session': session}
            )
            letter_serializer.is_valid(raise_exception=True)
            letter_serializer.save()

        # 4. Сохраняем статистику биграмм
        for data in bigram_stats_data:
            bigram_serializer = BigramStatsSerializer(
                data=data,
                context={'session': session}
            )
            bigram_serializer.is_valid(raise_exception=True)
            bigram_serializer.save()

        return session
