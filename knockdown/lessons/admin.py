from django.contrib import admin
from .models import Lesson, UserLessonProgress, DictionaryWord

admin.site.register(Lesson)
admin.site.register(UserLessonProgress)
admin.site.register(DictionaryWord)
