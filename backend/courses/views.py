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
from .services import PronunciationService # Added for refactoring
from .services import RecommendationService # Added for refactoring
# import openai # Removed as OpenAI calls are now in PronunciationService
from django.conf import settings
import os
from django.utils import timezone

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
            # Defaults are handled by the model's mark_as_complete or if UserProgress is newly created.
            # If creating, we want it complete. If getting, mark_as_complete handles existing.
        )
        
        progress.mark_as_complete() # Use the new model method
        
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
            # Defaults can be set if a new progress entry implies a certain score,
            # otherwise, update_score will handle it.
            # For get_or_create, if 'created' is true, 'progress' is a new object.
            # We might want to initialize its score if 'score' isn't part of defaults or is 0.
            # However, the current logic in update_score handles max(self.score, new_score).
            defaults={'score': 0} # Initialize score to 0 if created, update_score will set it.
        )
        
        try:
            score_int = int(score) # Ensure score is an integer
        except ValueError:
            return Response({"error": "Invalid score format"}, status=status.HTTP_400_BAD_REQUEST)

        progress.update_score(score_int) # Use the new model method
        
        serializer = UserProgressSerializer(progress)
        return Response(serializer.data)

class UserProgressViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

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

class PronunciationExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PronunciationExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PronunciationExercise.objects.filter(
            lesson__course__user=self.request.user
        )

class PronunciationAttemptViewSet(viewsets.ModelViewSet):
    serializer_class = PronunciationAttemptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PronunciationAttempt.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        attempt = serializer.save(user=self.request.user)
        
        # Instantiate the service
        pronunciation_service = PronunciationService()

        # Call the service to process the attempt
        # TODO: The language parameter should ideally be dynamic (e.g., from UserPreferences or Course settings)
        pronunciation_service.process_pronunciation_attempt(attempt, language="en")

        # The 'attempt' object is modified and saved by the PronunciationService,
        # so no explicit save is needed here unless the service contract changes.
        # If the service raised an exception that wasn't caught and handled by saving
        # error details to the attempt, then the original serializer.save() result would persist.
        # The current service implementation saves error details to the attempt object.

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

class UserXPViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserXPSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserXP.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def add_xp(self, request):
        amount_str = request.data.get('amount', '0') # Get amount as string
        try:
            amount = int(amount_str) # Convert to integer
            if amount < 0: # Optional: disallow negative XP amounts if that's a business rule
                return Response({"error": "Amount cannot be negative"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid amount provided"}, status=status.HTTP_400_BAD_REQUEST)

        user_xp, created = UserXP.objects.get_or_create(user=request.user)
        # The UserXP.add_xp() method now handles achievement checks internally.
        user_xp.add_xp(amount)
        
        serializer = self.get_serializer(user_xp)
        return Response(serializer.data)

    # _check_achievements method removed, logic moved to UserXP model.
    # _award_achievement method removed, logic moved to UserXP model.

class UserPreferencesViewSet(viewsets.ModelViewSet):
    serializer_class = UserPreferencesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserPreferences.objects.get_or_create(user=self.request.user)[0]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class LessonRecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = LessonRecommendationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LessonRecommendation.objects.filter(user=self.request.user)

    # _calculate_lesson_score method removed, logic moved to RecommendationService

    @action(detail=False, methods=['get'])
    def generate_recommendations(self, request):
        user = request.user
        preferences = UserPreferences.objects.get_or_create(user=user)[0]
        user_progress = UserProgress.objects.filter(user=user)

        recommendation_service = RecommendationService() # Instantiate the service

        # Clear existing recommendations
        LessonRecommendation.objects.filter(user=user).delete()

        # Get all lessons
        lessons = Lesson.objects.all() # Consider filtering for active/relevant lessons

        # Calculate scores and create recommendations
        recommendations = []
        for lesson in lessons:
            # Call the service method
            score, reason = recommendation_service.calculate_lesson_score(lesson, preferences, user_progress)
            if score > 0:
                recommendations.append(
                    LessonRecommendation(
                        user=user,
                        lesson=lesson,
                        score=score,
                        reason=reason
                    )
                )

        # Bulk create recommendations
        LessonRecommendation.objects.bulk_create(recommendations)

        # Return top recommendations
        serializer = self.get_serializer(recommendations[:5], many=True)
        return Response(serializer.data)

class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return NotificationPreference.objects.get_or_create(user=self.request.user)[0]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.mark_as_read() # Use the new model method
        return Response({'status': 'success', 'message': 'Notification marked as read.'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(read=True)
        return Response({'status': 'success'})

class WordOfTheDayViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WordOfTheDaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Use the new manager method to get today's word
        today_word = WordOfTheDay.objects.get_today()
        if today_word:
            # Return a queryset containing only today's word, or an empty queryset
            return WordOfTheDay.objects.filter(pk=today_word.pk)
        return WordOfTheDay.objects.none()