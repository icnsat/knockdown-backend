from rest_framework import serializers
from .models import Lesson, UserLessonProgress
from django.utils import timezone


class LessonSerializer(serializers.ModelSerializer):
    """Базовый CRUD для уроков для админов"""
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'content',
            'difficulty_level', 'lesson_type', 'order_index',
            'required_speed', 'required_accuracy',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_difficulty_level(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError(
                "Сложность должна быть от 1 до 10"
            )
        return value

    def validate_required_speed(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Скорость не может быть отрицательной"
            )
        return value

    def validate_required_accuracy(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Точность должна быть от 0 до 100%"
            )
        return value


class LessonDetailSerializer(LessonSerializer):
    """Урок с детальной информацией о прогрессе пользователя"""
    user_progress = serializers.SerializerMethodField()
    is_unlocked = serializers.SerializerMethodField()

    class Meta(LessonSerializer.Meta):
        fields = LessonSerializer.Meta.fields + [
            'user_progress', 'is_unlocked'
        ]

    def get_user_progress(self, obj):
        """Добавляет прогресс текущего пользователя"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserLessonProgress.objects.get(
                    user=request.user,
                    lesson=obj
                )
                return UserLessonProgressSerializer(progress).data
            except UserLessonProgress.DoesNotExist:
                return None
        return None

    def get_is_unlocked(self, obj):
        """Проверяет, доступен ли урок пользователю"""
        if obj.order_index == 1:
            return True  # первый урок всегда доступен

        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Урок доступен если предыдущий пройден
            prev_lesson = Lesson.objects.filter(
                order_index=obj.order_index - 1
            ).first()

            if prev_lesson:
                try:
                    prev_progress = UserLessonProgress.objects.get(
                        user=request.user,
                        lesson=prev_lesson
                    )
                    return prev_progress.is_passed
                except UserLessonProgress.DoesNotExist:
                    return False
        return False


class LessonListSerializer(serializers.ModelSerializer):
    """Упрощенный для списка уроков (включает данные об is_passed)"""
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'description', 'difficulty_level',
            'lesson_type', 'order_index', 'progress'
        ]

    def get_progress(self, obj):
        """Только минимальная информация о прогрессе"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = UserLessonProgress.objects.get(
                    user=request.user,
                    lesson=obj
                )
                return {
                    'is_passed': progress.is_passed,
                    'best_speed': progress.best_speed,
                    'completion_count': progress.completion_count
                }
            except UserLessonProgress.DoesNotExist:
                return None
        return None


'''
class UserLessonProgressSerializer(serializers.ModelSerializer):
    """DELETED - Ручное управление прогрессом пользователя"""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_type = serializers.CharField(
        source='lesson.lesson_type',
        read_only=True
    )

    class Meta:
        model = UserLessonProgress
        fields = [
            'id', 'user', 'lesson', 'lesson_title', 'lesson_type',
            'best_speed', 'best_accuracy', 'completion_count',
            'last_completed_at', 'is_passed', 'passed_at'
        ]
        read_only_fields = [
            'id', 'user', 'lesson', 'lesson_title', 'lesson_type',
            'passed_at'  # passed_at устанавливается автоматически
        ]

    def validate(self, data):
        """Проверяем логику обновления прогресса"""
        instance = self.instance

        if instance:
            # При обновлении проверяем, что лучшие результаты улучшаются
            if ('best_speed' in data and
               data['best_speed'] < instance.best_speed):
                raise serializers.ValidationError({
                    'best_speed': 'Новая скорость должна быть выше предыдущей'
                })

            if ('best_accuracy' in data and
               data['best_accuracy'] < instance.best_accuracy):
                raise serializers.ValidationError({
                    'best_accuracy':
                    'Новая точность должна быть выше предыдущей'
                })

        return data

    def update(self, instance, validated_data):
        """Автоматически устанавливаем passed_at при прохождении"""
        if 'is_passed' in validated_data and validated_data['is_passed']:
            if not instance.is_passed:  # только если раньше не был пройден
                validated_data['passed_at'] = timezone.now()

        return super().update(instance, validated_data)


class LessonProgressUpdateSerializer(serializers.Serializer):
    """REPLACED - Автоматическое обновление прогресса после тренировки"""
    lesson_id = serializers.IntegerField()
    speed = serializers.IntegerField(min_value=0)
    accuracy = serializers.FloatField(min_value=0, max_value=100)

    def update_progress(self, user):
        """Основная логика обновления прогресса"""
        lesson_id = self.validated_data['lesson_id']
        speed = self.validated_data['speed']
        accuracy = self.validated_data['accuracy']

        lesson = Lesson.objects.get(id=lesson_id)

        # Получаем или создаем прогресс
        progress, created = UserLessonProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'best_speed': speed,
                'best_accuracy': accuracy,
                'completion_count': 1,
                'last_completed_at': timezone.now()
            }
        )

        if not created:
            # Обновляем лучшие результаты
            if speed > progress.best_speed:
                progress.best_speed = speed

            if accuracy > progress.best_accuracy:
                progress.best_accuracy = accuracy

            progress.completion_count += 1
            progress.last_completed_at = timezone.now()

        # Проверяем выполнение требований
        if (speed >= lesson.required_speed and
           accuracy >= lesson.required_accuracy and
           not progress.is_passed):
            progress.is_passed = True
            progress.passed_at = timezone.now()

        progress.save()
        return progress
'''


class UserLessonProgressSerializer(serializers.ModelSerializer):
    """Только для чтения прогресса. Создание/обновление - автоматически."""
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    lesson_type = serializers.CharField(
        source='lesson.lesson_type',
        read_only=True
    )
    required_speed = serializers.IntegerField(
        source='lesson.required_speed',
        read_only=True
    )
    required_accuracy = serializers.FloatField(
        source='lesson.required_accuracy',
        read_only=True
    )

    class Meta:
        model = UserLessonProgress
        fields = [
            'id',
            'lesson',
            'lesson_title',
            'lesson_type',
            'required_speed',
            'required_accuracy',
            'best_speed',
            'best_accuracy',
            'completion_count',
            'last_completed_at',
            'is_passed',
            'passed_at',
        ]
        read_only_fields = fields


'''
class GeneratedLessonSerializer(serializers.Serializer):
    """Для ответа с сгенерированным уроком"""
    title = serializers.CharField()
    content = serializers.CharField()
    difficulty_level = serializers.IntegerField()
    lesson_type = serializers.CharField()
    target_letters = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    target_bigrams = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    word_count = serializers.IntegerField()
 
    def create(self, validated_data):
        """Создает временный урок (не сохраняет в БД)"""
        # Можно сохранить как временную запись или просто вернуть данные
        return validated_data
'''
