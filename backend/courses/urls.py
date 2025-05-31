from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    LessonViewSet,
    UserProgressViewSet,
    PronunciationExerciseViewSet,
    PronunciationAttemptViewSet,
    LeaderboardViewSet,
    UserXPViewSet,
    UserPreferencesViewSet,
    LessonRecommendationViewSet,
    NotificationPreferenceViewSet,
    NotificationViewSet,
    WordOfTheDayViewSet,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'progress', UserProgressViewSet, basename='progress')
router.register(r'pronunciation-exercises', PronunciationExerciseViewSet, basename='pronunciation-exercise')
router.register(r'pronunciation-attempts', PronunciationAttemptViewSet, basename='pronunciation-attempt')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'user-xp', UserXPViewSet, basename='user-xp')
router.register(r'preferences', UserPreferencesViewSet, basename='preferences')
router.register(r'recommendations', LessonRecommendationViewSet, basename='recommendations')
router.register(r'notification-preferences', NotificationPreferenceViewSet, basename='notification-preferences')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'word-of-day', WordOfTheDayViewSet, basename='word-of-day')

urlpatterns = [
    path('', include(router.urls)),
] 