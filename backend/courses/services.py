from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Notification, NotificationPreference, UserXP, WordOfTheDay, UserAchievement
import openai
from django.core.files.storage import default_storage

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
        preferences = NotificationPreference.objects.get(user=notification.user)
        notification_type = preferences.notification_types.get(notification.type, 'BOTH')

        if notification_type in ['EMAIL', 'BOTH'] and preferences.email_enabled:
            NotificationService.send_email(notification)

        if notification_type in ['PUSH', 'BOTH'] and preferences.push_enabled:
            NotificationService.send_push(notification)

        notification.sent = True
        notification.sent_at = timezone.now()
        notification.save()

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
        # This is a placeholder for FCM implementation
        # You would need to implement the actual FCM integration
        pass

    @staticmethod
    def send_daily_reminder(user):
        """Send a daily learning reminder."""
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

    @staticmethod
    def send_word_of_day(user):
        """Send the word of the day."""
        preferences = NotificationPreference.objects.get(user=user)
        if not preferences.email_enabled and not preferences.push_enabled:
            return

        word = WordOfTheDay.objects.filter(date=timezone.now().date()).first()
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

    @staticmethod
    def send_progress_update(user):
        """Send a progress update notification."""
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

    @staticmethod
    def send_streak_alert(user):
        """Send a streak alert notification."""
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

class PronunciationService:
    @staticmethod
    def process_pronunciation_attempt(attempt):
        try:
            openai.api_key = settings.OPENAI_API_KEY
            
            # Transcribe audio using Whisper
            with default_storage.open(attempt.audio_file.name, 'rb') as audio_file:
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

class AchievementService:
    @staticmethod
    def check_and_award_achievements(user_xp):
        # Check streak achievements
        if user_xp.streak_days == 3:
            AchievementService._award_achievement(user_xp, 'STREAK_3', 100)
        elif user_xp.streak_days == 7:
            AchievementService._award_achievement(user_xp, 'STREAK_7', 300)
        elif user_xp.streak_days == 30:
            AchievementService._award_achievement(user_xp, 'STREAK_30', 1000)

        # Check level up achievement
        if user_xp.level > 1:
            AchievementService._award_achievement(user_xp, 'LEVEL_UP', 200)

    @staticmethod
    def _award_achievement(user_xp, achievement_type, xp_reward):
        achievement, created = UserAchievement.objects.get_or_create(
            user=user_xp.user,
            type=achievement_type,
            defaults={'xp_reward': xp_reward}
        )
        if created:
            user_xp.add_xp(xp_reward) 