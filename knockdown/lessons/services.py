import random
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
from .models import DictionaryWord
from stats.models import DailyLetterStatistics, DailyBigramStatistics


class LessonGenerator:
    """Генератор персонализированных уроков"""

    def __init__(self, user):
        self.user = user

    def generate(
            self, type='auto', difficulty=1, length=200,
            target_letters=None, target_bigrams=None
    ):
        """Основной метод генерации"""

        if type == 'bigrams' or (type == 'auto' and target_bigrams):
            return self.generate_bigram_lesson(
                target_bigrams, difficulty, length
            )
        else:
            return self.generate_letter_lesson(
                target_letters, difficulty, length
            )

    def get_problem_letters(
            self, limit=5, days_delta=7, min_occurrences=10, error_threshold=15
            ):
        """
        Анализ дневной статистики - буквы с ошибками > threshold%
        с каскадным расширением периода
        """

        # Пробуем разные периоды: 7, 14, 30, 90 дней, все время
        periods = [7, 14, 30, 90, 365, None]  # None = все время

        for days in periods:
            if days:
                start_date = timezone.now().date() - timedelta(days=days)
                stats = DailyLetterStatistics.objects.filter(
                    user=self.user,
                    date__gte=start_date
                )
            else:
                # Все время
                stats = DailyLetterStatistics.objects.filter(user=self.user)

            if stats.exists():
                # Агрегируем
                aggregated = stats.values('letter').annotate(
                    total_occ=Sum('total_occurrences'),
                    total_err=Sum('total_errors')
                ).filter(total_occ__gte=min_occurrences)

                problem_letters = []
                for stat in aggregated:
                    error_rate = stat['total_err'] * 100 / stat['total_occ']
                    if error_rate > error_threshold:
                        problem_letters.append({
                            'letter': stat['letter'],
                            'error_rate': error_rate
                            })

                if problem_letters:
                    # Сортируем по убыванию ошибок
                    problem_letters.sort(
                        key=lambda x: x['error_rate'], reverse=True
                    )
                    return [item['letter'] for item in problem_letters[:limit]]

        # 3. Если вообще нет статистики - возвращаем частотные буквы
        return ['а', 'о', 'е', 'и', 'н'][:limit]  # самые частые буквы в русском

    def get_problem_bigrams(
            self, limit=5, days_delta=7, min_occurrences=5, error_threshold=15
            ):
        """
        Анализ дневной статистики - биаграммы с ошибками > threshold%
        с каскадным расширением периода
        """

        periods = [7, 14, 30, 90, 365, None]

        for days in periods:
            if days:
                start_date = timezone.now().date() - timedelta(days=days)
                stats = DailyBigramStatistics.objects.filter(
                    user=self.user,
                    date__gte=start_date
                )
            else:
                stats = DailyBigramStatistics.objects.filter(user=self.user)

            if stats.exists():
                aggregated = stats.values('bigram').annotate(
                    total_occ=Sum('total_occurrences'),
                    total_err=Sum('total_errors')
                ).filter(total_occ__gte=min_occurrences)

                problem_bigrams = []
                for stat in aggregated:
                    error_rate = stat['total_err'] * 100 / stat['total_occ']
                    if error_rate > error_threshold:
                        problem_bigrams.append({
                            'bigram': stat['bigram'],
                            'error_rate': error_rate
                            })

                if problem_bigrams:
                    # Сортируем по убыванию процента ошибок
                    problem_bigrams.sort(
                        key=lambda x: x['error_rate'], reverse=True
                    )
                    # Берем ТОП-N
                    return [item['bigram'] for item in problem_bigrams[:limit]]

        # Если нет статистики - частотные биграммы русского языка
        return ['ст', 'но', 'то', 'на', 'по'][:limit]

    def find_words_by_letters(self, letters, limit=30):
        """Поиск слов в DictionaryWord по буквам"""

        queryset = DictionaryWord.objects.filter(length__range=(3, 15))
        for letter in letters:
            queryset = queryset.filter(letters__contains=letter)
        return list(queryset.values_list('word', flat=True)[:limit])

    def find_words_by_bigrams(self, bigrams, limit=30):
        """Поиск слов в DictionaryWord по биграммам"""

        queryset = DictionaryWord.objects.filter(
            bigrams__overlap=bigrams
        ).order_by('-frequency')[:limit]
        return list(queryset.values_list('word', flat=True))

    def build_lesson_text(self, words, length=200):
        """Составляет текст из слов"""

        selected = random.sample(words, min(len(words), length//5))
        return ' '.join(selected)

    def generate_letter_lesson(
            self, target_letters=None, difficulty=3, length=200
    ):
        """Урок на основе проблемных букв"""

        if not target_letters:
            target_letters = self.get_problem_letters(limit=5)

        words = self.find_words_by_letters(target_letters)
        text = self.build_lesson_text(words, length)

        return {
            'title': f'Тренировка букв: {", ".join(target_letters)}',
            'content': text,
            'lesson_type': 'problem_letters',
            'difficulty_level': difficulty,
            'target': target_letters,
            'required_speed': 0,
            'required_accuracy': 0.0,
            'word_count': len(words),
        }

    def generate_bigram_lesson(
            self, target_bigrams=None, difficulty=3, length=200
    ):
        """Урок на основе проблемных биаграмм"""

        if not target_bigrams:
            target_bigrams = self.get_problem_bigrams(limit=5)

        words = self.find_words_by_bigrams(target_bigrams)
        text = self.build_lesson_text(words, length)

        return {
            'title': f'Тренировка биграмм: {", ".join(target_bigrams)}',
            'content': text,
            'lesson_type': 'bigrams',
            'difficulty_level': difficulty,
            'target': target_bigrams,
            'required_speed': 0,
            'required_accuracy': 0.0,
            'word_count': len(words),
        }
