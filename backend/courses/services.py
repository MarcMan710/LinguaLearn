from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
# Updated to include models needed for RecommendationService
from .models import (
    Notification, NotificationPreference, UserXP, WordOfTheDay,
    Lesson, UserPreferences, UserProgress # Added Lesson, UserPreferences, UserProgress
)
import requests
import json

import openai

class NotificationService:
    @staticmethod
    def create_notification(user, type, title, message, data=None):
        """Create a new notification for a user."""
        notification = Notification.objects.create(
            user=user,
            type=type,
            title=title,
            message=message,
            data=data or {}
        )
        return notification

    @staticmethod
    def send_notification(notification):
        """Send a notification through the user's preferred channels."""
        try:
            preferences = NotificationPreference.objects.get(user=notification.user)
            notification_type_prefs = getattr(preferences, 'notification_types', {})
            notification_type = notification_type_prefs.get(notification.type, 'BOTH')

            if notification_type in ['EMAIL', 'BOTH'] and preferences.email_enabled:
                NotificationService.send_email(notification)

            if notification_type in ['PUSH', 'BOTH'] and preferences.push_enabled:
                NotificationService.send_push(notification)

            notification.mark_as_sent() # Use the new model method

        except NotificationPreference.DoesNotExist:
            # Log or handle missing preferences if necessary
            # For example, you might still attempt to send critical notifications
            # or log that preferences are missing for this user.
            # logger.warning(f"NotificationPreference not found for user {notification.user.id}. Notification {notification.id} may not be sent as per preference.")
            pass
        except Exception as e:
            # Log other exceptions during notification sending
            # logger.error(f"Error sending notification {notification.id} for user {notification.user.id}: {str(e)}")
            pass


    @staticmethod
    def send_email(notification):
        """Send an email notification."""
        send_mail(
            subject=notification.title,
            message=notification.message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[notification.user.email],
            fail_silently=True
        )

    @staticmethod
    def send_push(notification):
        """Send a push notification using a service like Firebase Cloud Messaging."""
        pass

    @staticmethod
    def send_daily_reminder(user):
        """Send a daily learning reminder."""
        try:
            preferences = NotificationPreference.objects.get(user=user)
            if not preferences.email_enabled and not preferences.push_enabled:
                return

            message = "Don't forget to practice today! Keep your streak going."
            NotificationService.create_notification(
                user=user,
                type='DAILY_REMINDER',
                title='Daily Learning Reminder',
                message=message
            )
        except NotificationPreference.DoesNotExist:
            pass

    @staticmethod
    def send_word_of_day(user):
        """Send the word of the day."""
        try:
            preferences = NotificationPreference.objects.get(user=user)
            if not preferences.email_enabled and not preferences.push_enabled:
                return

            word = WordOfTheDay.objects.get_today() # Use the new manager method
            if not word:
                return

            message = f"Today's word: {word.word}\nMeaning: {word.translation}\nExample: {word.example_sentence}"
            NotificationService.create_notification(
                user=user,
                type='WORD_OF_DAY',
                title='Word of the Day',
                message=message,
                data={'word': word.word, 'translation': word.translation}
            )
        except NotificationPreference.DoesNotExist:
            pass


    @staticmethod
    def send_progress_update(user):
        """Send a progress update notification."""
        try:
            preferences = NotificationPreference.objects.get(user=user)
            if not preferences.email_enabled and not preferences.push_enabled:
                return

            user_xp = UserXP.objects.get(user=user)
            message = f"You're making great progress! Current level: {user_xp.level}, Total XP: {user_xp.total_xp}"
            NotificationService.create_notification(
                user=user,
                type='PROGRESS_UPDATE',
                title='Progress Update',
                message=message,
                data={'level': user_xp.level, 'total_xp': user_xp.total_xp}
            )
        except NotificationPreference.DoesNotExist:
            pass
        except UserXP.DoesNotExist:
            pass


    @staticmethod
    def send_streak_alert(user):
        """Send a streak alert notification."""
        try:
            preferences = NotificationPreference.objects.get(user=user)
            if not preferences.email_enabled and not preferences.push_enabled:
                return

            user_xp = UserXP.objects.get(user=user)
            if user_xp.streak_days > 0:
                message = f"Keep your {user_xp.streak_days}-day streak going! Don't break the chain!"
                NotificationService.create_notification(
                    user=user,
                    type='STREAK_ALERT',
                    title='Streak Alert',
                    message=message,
                    data={'streak_days': user_xp.streak_days}
                )
        except NotificationPreference.DoesNotExist:
            pass
        except UserXP.DoesNotExist:
            pass

class PronunciationService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in Django settings.")
        openai.api_key = settings.OPENAI_API_KEY

    def process_pronunciation_attempt(self, attempt, language="en"):
        if not hasattr(attempt, 'audio_file') or not hasattr(attempt.audio_file, 'path') or not attempt.audio_file.path:
            attempt.feedback = "Audio file not found, is invalid, or path is missing. Please re-upload."
            attempt.transcription = "Audio file processing error."
            attempt.accuracy_score = 0.0
            if hasattr(attempt, 'save'): attempt.save()
            return

        if not hasattr(attempt, 'exercise') or not attempt.exercise or \
           not hasattr(attempt.exercise, 'word') or not attempt.exercise.word or \
           not hasattr(attempt.exercise, 'correct_pronunciation') or not attempt.exercise.correct_pronunciation:
            pass

        try:
            with open(attempt.audio_file.path, 'rb') as audio_file_obj:
                transcription_response = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file_obj,
                    language=language
                )
            attempt.transcription = transcription_response['text']

            if not hasattr(attempt, 'exercise') or not attempt.exercise or \
               not hasattr(attempt.exercise, 'word') or not attempt.exercise.word or \
               not hasattr(attempt.exercise, 'correct_pronunciation') or not attempt.exercise.correct_pronunciation:
                attempt.feedback = "Exercise data (word or correct pronunciation) is missing. Transcription was successful, but specific feedback cannot be generated."
                attempt.accuracy_score = 0.5
                if hasattr(attempt, 'save'): attempt.save()
                return

            feedback_prompt = f"""
            You are a language pronunciation coach.
            A student is practicing the word/phrase: "{attempt.exercise.word}".
            The student's pronunciation was transcribed as: "{attempt.transcription}".
            The target pronunciation (how it should sound) is like: "{attempt.exercise.correct_pronunciation}".

            Please provide feedback on the student's pronunciation. Focus on:
            1. Overall accuracy: How close was the transcription to the target word/phrase?
            2. Specific mispronounced sounds or phonemes: Identify any sounds that were clearly different from the target.
            3. Suggestions for improvement: Offer concrete tips (e.g., "try to make the 'th' sound by placing your tongue between your teeth").
            4. Positive reinforcement: If parts were good, mention them.

            Keep the feedback concise, constructive, and easy for a language learner to understand.
            """

            feedback_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a language pronunciation expert providing feedback to a language learner."},
                    {"role": "user", "content": feedback_prompt}
                ]
            )

            if feedback_response.choices and len(feedback_response.choices) > 0 and feedback_response.choices[0].message:
                attempt.feedback = feedback_response.choices[0].message['content'].strip()
            else:
                attempt.feedback = "Could not retrieve feedback from OpenAI at this time. Please try again later."

            normalized_transcription = attempt.transcription.lower().strip().rstrip('.,!?')
            normalized_exercise_word = attempt.exercise.word.lower().strip()

            if normalized_transcription == normalized_exercise_word:
                attempt.accuracy_score = 0.95
            else:
                attempt.accuracy_score = 0.65

            if hasattr(attempt, 'save'): attempt.save()

        except openai.APIError as e:
            error_detail = "Unknown API error."
            error_status_code = e.status_code if hasattr(e, 'status_code') else 'N/A'
            if hasattr(e, 'json_body') and e.json_body and 'error' in e.json_body and e.json_body['error']:
                error_detail = e.json_body['error'].get('message', str(e.json_body['error']))
            elif e.http_body:
                 error_detail = f"Non-JSON error response from API: {e.http_body[:500]}"

            attempt.feedback = f"There was an issue with the AI service (Status: {error_status_code}). Please try again. If the problem persists, contact support. Detail: {error_detail}"
            attempt.accuracy_score = 0.0
            if not attempt.transcription:
                 attempt.transcription = "Transcription failed due to API error."
            if hasattr(attempt, 'save'): attempt.save()

        except FileNotFoundError:
            attempt.feedback = f"Audio file not found at the specified path: {getattr(attempt.audio_file, 'path', 'No path provided')}. Please ensure the file was uploaded correctly and try again."
            attempt.accuracy_score = 0.0
            if not attempt.transcription:
                 attempt.transcription = "Transcription failed: missing audio file."
            if hasattr(attempt, 'save'): attempt.save()

        except Exception as e:
            attempt.feedback = f"An unexpected error occurred during pronunciation processing: {str(e)}. Please contact support if this issue continues."
            attempt.accuracy_score = 0.0
            if not attempt.transcription:
                 attempt.transcription = "Transcription failed due to an unexpected error."
            if hasattr(attempt, 'save'): attempt.save()

# New RecommendationService
class RecommendationService:
    def calculate_lesson_score(self, lesson, user_preferences, user_progress):
        """
        Calculates a recommendation score for a given lesson based on user preferences
        and progress.

        Args:
            lesson: The Lesson object to score.
            user_preferences: The UserPreferences object for the user.
            user_progress: A queryset of UserProgress objects for the user.

        Returns:
            A tuple (score, reason_string).
        """
        score = 0.0
        reasons = []

        # Ensure necessary objects and their attributes are available
        if not all([lesson, user_preferences, user_progress is not None]): # user_progress can be an empty queryset
            return 0.0, "Missing core data for scoring."

        # Level matching
        if hasattr(lesson, 'course') and lesson.course and hasattr(lesson.course, 'level') and \
           hasattr(user_preferences, 'current_level') and user_preferences.current_level is not None and \
           lesson.course.level == user_preferences.current_level:
            score += 2.0
            reasons.append("Matches your current level")

        # Preferred lesson type
        if hasattr(lesson, 'type') and lesson.type and \
           hasattr(user_preferences, 'preferred_lesson_types') and \
           isinstance(user_preferences.preferred_lesson_types, list) and \
           lesson.type in user_preferences.preferred_lesson_types:
            score += 1.5
            reasons.append("Matches your preferred learning style")

        # Weak areas
        if hasattr(user_preferences, 'weak_areas') and isinstance(user_preferences.weak_areas, list) and \
           hasattr(lesson, 'title') and lesson.title:
            try:
                # Ensure all items in weak_areas are strings before lowercasing.
                # Filter out non-string elements if necessary.
                weak_areas_str = [area for area in user_preferences.weak_areas if isinstance(area, str)]
                if any(area.lower() in lesson.title.lower() for area in weak_areas_str):
                    score += 2.0
                    reasons.append("Helps improve your weak areas")
            except AttributeError: # Handles case where an item in weak_areas might not be a string
                reasons.append("Could not fully process weak areas due to data format.")


        # Progress-based scoring
        # Ensure user_progress is a queryset and lesson.order is usable
        if hasattr(user_progress, 'filter') and hasattr(lesson, 'order') and isinstance(lesson.order, int):
            completed_lessons_count = user_progress.filter(completed=True).count()
            if completed_lessons_count > 0: # Only apply if user has completed some lessons
                if lesson.order > completed_lessons_count:
                    score += 1.0
                    reasons.append("Builds upon your completed lessons")

        # Learning goal alignment
        if hasattr(user_preferences, 'learning_goal') and user_preferences.learning_goal and \
           hasattr(lesson, 'description') and lesson.description:
            try:
                if user_preferences.learning_goal.lower() in lesson.description.lower():
                    score += 1.5
                    reasons.append("Aligns with your learning goal")
            except AttributeError: # Handles case where learning_goal or description might not be strings
                 reasons.append("Could not fully process learning goal due to data format.")


        return score, " | ".join(reasons) if reasons else "General recommendation."
```
