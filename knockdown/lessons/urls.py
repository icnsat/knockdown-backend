from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('lessons', views.LessonViewSet)
# router.register('progress', views.UserLessonProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'progress/',
        views.UserLessonProgressListAPIView.as_view()
    ),  # Список всех + удалить все
    path(
        'progress/<int:progress_id>/',
        views.UserLessonProgressDetailAPIView.as_view()
    ),  # Конкретный прогресс

    # path('generate/', views.GenerateLessonView.as_view()),
    # path('recommended/', views.RecommendedLessonsView.as_view()), # Доп. функционал
]
