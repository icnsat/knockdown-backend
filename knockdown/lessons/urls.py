from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('lessons', views.LessonViewSet)
router.register('progress', views.UserLessonProgressViewSet, basename='progress')

urlpatterns = [
    path('', include(router.urls)),
    # path('generate/', views.GenerateLessonView.as_view()),
    # path('recommended/', views.RecommendedLessonsView.as_view()), # Доп. функционал
]