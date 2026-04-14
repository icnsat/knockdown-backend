import os
import sys
import django
from pathlib import Path

# Django setup
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'knockdown.settings')
django.setup()

from lessons.models import DictionaryWord


def load_words_from_file(filename):
    """Чтение слов из файла"""
    file_path = BASE_DIR / 'scripts' / filename
    words = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip().lower()
            # if 3 <= len(word) <= 12:  # only reasonable words
            words.append(word)

    print(f"Прочитано {len(words)} слов из файла")
    return words


def clean_db():
    """Удаление всех записей из словаря"""
    deleted_count, _ = DictionaryWord.objects.all().delete()
    print(f"Удалено записей: {deleted_count}")


def save_words_to_db(words):
    """Создание записей в БД"""
    created_count = 0
    skipped_count = 0

    for word in words:
        obj, created = DictionaryWord.objects.get_or_create(
            word=word,
            defaults={
                'length': len(word),
                'frequency': 1,  # initial value
                'letters': ''.join(sorted(set(word))),
                'bigrams': [word[i:i+2] for i in range(len(word)-1)]
            }
        )
        if created:
            created_count += 1
        else:
            skipped_count += 1

        # Progress every 1000 words
        if created_count % 1000 == 0 and created_count != 0:
            print(f"Обработано {created_count} слов...")
    return created_count, skipped_count


if __name__ == '__main__':
    # print("Очищение словаря...")
    # clean_db()

    print("\nЗаполнение словаря...")
    words = load_words_from_file('russian_dict.txt')
    created, skipped = save_words_to_db(words)

    print("\nИтог заполнения:")
    print(f"   - Создано новых записей: {created}")
    print(f"   - Пропущено (уже были в БД): {skipped}")
    print(f"   - Всего в БД: {DictionaryWord.objects.count()}")
