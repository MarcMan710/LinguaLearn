from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Notification, NotificationPreference, UserXP, WordOfTheDay
import requests
import json

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