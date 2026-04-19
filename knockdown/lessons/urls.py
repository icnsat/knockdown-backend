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

urlpatterns = [
    path('', include(router.urls)),
    path(
        'progress/',
        UserLessonProgressListAPIView.as_view()
    ),
    path(
        'progress/<int:progress_id>/',
        UserLessonProgressDetailAPIView.as_view()
    ),

    path('generate/', GenerateLessonView.as_view()),
    # path('recommended/', views.RecommendedLessonsView.as_view()), # Доп. функционал
]
