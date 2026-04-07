from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('sessions', views.TrainingSessionViewSet, basename='session')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.DashboardStatsView.as_view()),
    path('daily/', views.DailyStatsView.as_view()),
    path('letters/', views.LetterStatsView.as_view()),
    path('bigrams/', views.BigramStatsView.as_view()),
]
