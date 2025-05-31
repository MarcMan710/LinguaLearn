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
import openai
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
        
        # Process audio with Whisper API
        try:
            openai.api_key = settings.OPENAI_API_KEY
            
            # Transcribe audio using Whisper
            with open(attempt.audio_file.path, 'rb') as audio_file:
                transcription = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Adjust based on target language
                )
            
            # Get feedback using GPT
            feedback_prompt = f"""
            Compare the pronunciation of "{attempt.exercise.word}" with the correct pronunciation "{attempt.exercise.correct_pronunciation}".
            Provide specific feedback on:
            1. Accuracy of pronunciation
            2. Areas for improvement
            3. Tips for better pronunciation
            """
            
            feedback_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a language pronunciation expert."},
                    {"role": "user", "content": feedback_prompt}
                ]
            )
            
            # Calculate accuracy score (simplified version)
            accuracy_score = 0.8  # This should be replaced with actual pronunciation comparison logic
            
            # Update attempt with results
            attempt.transcription = transcription['text']
            attempt.feedback = feedback_response.choices[0].message.content
            attempt.accuracy_score = accuracy_score
            attempt.save()
            
        except Exception as e:
            # Handle errors appropriately
            attempt.feedback = f"Error processing audio: {str(e)}"
            attempt.save()

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
        amount = request.data.get('amount', 0)
        user_xp, created = UserXP.objects.get_or_create(user=request.user)
        user_xp.add_xp(amount)
        
        # Check for achievements
        self._check_achievements(user_xp)
        
        serializer = self.get_serializer(user_xp)
        return Response(serializer.data)

    def _check_achievements(self, user_xp):
        # Check streak achievements
        if user_xp.streak_days == 3:
            self._award_achievement(user_xp, 'STREAK_3', 100)
        elif user_xp.streak_days == 7:
            self._award_achievement(user_xp, 'STREAK_7', 300)
        elif user_xp.streak_days == 30:
            self._award_achievement(user_xp, 'STREAK_30', 1000)

        # Check level up achievement
        if user_xp.level > 1:
            self._award_achievement(user_xp, 'LEVEL_UP', 200)

    def _award_achievement(self, user_xp, achievement_type, xp_reward):
        achievement, created = UserAchievement.objects.get_or_create(
            user=user_xp.user,
            type=achievement_type,
            defaults={'xp_reward': xp_reward}
        )
        if created:
            user_xp.add_xp(xp_reward)

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
            score += 2.0
            reasons.append("Helps improve your weak areas")

        # Progress-based scoring
        completed_lessons = user_progress.filter(completed=True).count()
        if completed_lessons > 0:
            # Prioritize lessons that build upon completed ones
            if lesson.order > completed_lessons:
                score += 1.0
                reasons.append("Builds upon your completed lessons")

        # Learning goal alignment
        if user_preferences.learning_goal.lower() in lesson.description.lower():
            score += 1.5
            reasons.append("Aligns with your learning goal")

        return score, " | ".join(reasons)

    @action(detail=False, methods=['get'])
    def generate_recommendations(self, request):
        user = request.user
        preferences = UserPreferences.objects.get_or_create(user=user)[0]
        user_progress = UserProgress.objects.filter(user=user)

        # Clear existing recommendations
        LessonRecommendation.objects.filter(user=user).delete()

        # Get all lessons
        lessons = Lesson.objects.all()

        # Calculate scores and create recommendations
        recommendations = []
        for lesson in lessons:
            score, reason = self._calculate_lesson_score(lesson, preferences, user_progress)
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
        notification.read = True
        notification.save()
        return Response({'status': 'success'})

    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        self.get_queryset().update(read=True)
        return Response({'status': 'success'})

class WordOfTheDayViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WordOfTheDaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WordOfTheDay.objects.filter(date=timezone.now().date()) 