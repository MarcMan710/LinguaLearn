from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Course, Lesson, UserProgress, PronunciationExercise, PronunciationAttempt, UserXP, UserAchievement, UserPreferences, LessonRecommendation, Notification, NotificationPreference, WordOfTheDay
from .serializers import (
    CourseSerializer, LessonSerializer, UserProgressSerializer,
    PronunciationExerciseSerializer, PronunciationAttemptSerializer,
    LeaderboardEntrySerializer, UserXPSerializer, UserPreferencesSerializer,
    LessonRecommendationSerializer, NotificationPreferenceSerializer,
    NotificationSerializer, WordOfTheDaySerializer
)
from .services import PronunciationService, AchievementService
from django.utils import timezone
from .mixins import UserQuerysetMixin

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.all()
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)

class LessonViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        lesson = self.get_object()
        user = request.user
        
        # Get or create user progress
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'completed': True, 'score': 100}
        )
        
        if not created:
            progress.completed = True
            progress.score = 100
            progress.save()
        
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        lesson = self.get_object()
        user = request.user
        score = request.data.get('score', 0)
        
        progress, created = UserProgress.objects.get_or_create(
            user=user,
            lesson=lesson,
            defaults={'score': score}
        )
        
        if not created:
            progress.score = max(progress.score, score)
            progress.save()
        
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)

class UserProgressViewSet(UserQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer

    @action(detail=False, methods=['get'])
    def completed_lessons(self, request):
        completed = self.get_queryset().filter(completed=True)
        serializer = self.get_serializer(completed, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def in_progress(self, request):
        in_progress = self.get_queryset().filter(completed=False)
        serializer = self.get_serializer(in_progress, many=True)
        return Response(serializer.data)

class PronunciationExerciseViewSet(UserQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = PronunciationExercise.objects.all()
    serializer_class = PronunciationExerciseSerializer

    def get_queryset(self):
        return PronunciationExercise.objects.filter(
            lesson__course__user=self.request.user
        )

class PronunciationAttemptViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    queryset = PronunciationAttempt.objects.all()
    serializer_class = PronunciationAttemptSerializer

    def perform_create(self, serializer):
        attempt = serializer.save(user=self.request.user)
        PronunciationService.process_pronunciation_attempt(attempt)

class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = UserXP.objects.all().order_by('-total_xp')
        
        # Filter by friends if specified
        friends_only = self.request.query_params.get('friends_only', 'false').lower() == 'true'
        if friends_only:
            # Get user's friends (implement your friend system logic here)
            friend_ids = []  # Replace with actual friend IDs
            queryset = queryset.filter(user_id__in=friend_ids)
        
        return queryset[:100]  # Limit to top 100

    @action(detail=False, methods=['get'])
    def my_rank(self, request):
        user_xp = UserXP.objects.get(user=request.user)
        serializer = self.get_serializer(user_xp)
        return Response(serializer.data)

class UserXPViewSet(UserQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = UserXP.objects.all()
    serializer_class = UserXPSerializer

    @action(detail=False, methods=['post'])
    def add_xp(self, request):
        amount = request.data.get('amount', 0)
        user_xp, created = UserXP.objects.get_or_create(user=self.request.user)
        user_xp.add_xp(amount)
        
        AchievementService.check_and_award_achievements(user_xp)
        
        serializer = self.get_serializer(user_xp)
        return Response(serializer.data)

class UserPreferencesViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    queryset = UserPreferences.objects.all()
    serializer_class = UserPreferencesSerializer

    def get_object(self):
        return UserPreferences.objects.get_or_create(user=self.request.user)[0]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LessonRecommendationViewSet(UserQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = LessonRecommendation.objects.all()
    serializer_class = LessonRecommendationSerializer

    def _calculate_lesson_score(self, lesson, user_preferences, user_progress):
        score = 0.0
        reasons = []

        # Level matching
        if lesson.course.level == user_preferences.current_level:
            score += 2.0
            reasons.append("Matches your current level")

        # Preferred lesson type
        if lesson.type in user_preferences.preferred_lesson_types:
            score += 1.5
            reasons.append("Matches your preferred learning style")

        # Weak areas
        if any(area in lesson.title.lower() for area in user_preferences.weak_areas):
            score += 1.0
            reasons.append("Addresses your weak areas")

        # Completed lessons (avoid recommending already completed lessons)
        if user_progress.filter(lesson=lesson, completed=True).exists():
            score -= 5.0  # Penalize already completed lessons
            reasons.append("Already completed")

        return score, reasons

    @action(detail=False, methods=['get'])
    def generate_recommendations(self, request):
        user = request.user
        user_preferences = UserPreferences.objects.get_or_create(user=user)[0]
        user_progress = UserProgress.objects.filter(user=user)

        all_lessons = Lesson.objects.all()
        recommendations = []

        for lesson in all_lessons:
            score, reasons = self._calculate_lesson_score(
                lesson, user_preferences, user_progress
            )
            if score > 0:
                recommendations.append({
                    'lesson': lesson,
                    'score': score,
                    'reason': ", ".join(reasons)
                })

        # Sort recommendations by score and limit to top N
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        serializer = LessonRecommendationSerializer(recommendations[:10], many=True)
        return Response(serializer.data)

class NotificationPreferenceViewSet(UserQuerysetMixin, viewsets.ModelViewSet):
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer

    def get_object(self):
        return NotificationPreference.objects.get_or_create(user=self.request.user)[0]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationViewSet(UserQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(read=True)
        return Response({'status': 'all notifications marked as read'})

class WordOfTheDayViewSet(UserQuerysetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = WordOfTheDay.objects.all()
    serializer_class = WordOfTheDaySerializer

    def get_queryset(self):
        return WordOfTheDay.objects.filter(user=self.request.user).order_by('-date')[:1] 