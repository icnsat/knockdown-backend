from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LessonViewSet,
    UserLessonProgressListAPIView,
    UserLessonProgressDetailAPIView,
    GenerateLessonView
)

router = DefaultRouter()
router.register('lessons', LessonViewSet)
# router.register('progress', views.UserLessonProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'progress/',
        UserLessonProgressListAPIView.as_view()
    ),  # Список всех + удалить все
    path(
        'progress/<int:progress_id>/',
        UserLessonProgressDetailAPIView.as_view()
    ),  # Конкретный прогресс

    path('generate/', GenerateLessonView.as_view()),
    # path('recommended/', views.RecommendedLessonsView.as_view()), # Доп. функционал
]
