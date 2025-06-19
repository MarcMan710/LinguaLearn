from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Course(models.Model):
    LEVEL_CHOICES = [
        ('A1', 'Beginner'),
        ('A2', 'Elementary'),
        ('B1', 'Intermediate'),
        ('B2', 'Upper Intermediate'),
        ('C1', 'Advanced'),
        ('C2', 'Mastery'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    TYPE_CHOICES = [
        ('VOCABULARY', 'Vocabulary'),
        ('GRAMMAR', 'Grammar'),
        ('LISTENING', 'Listening'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class VocabularyItem(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='vocabulary_items')
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=200)
    example_sentence = models.TextField()
    pronunciation = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.word} - {self.translation}"

class GrammarRule(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='grammar_rules')
    title = models.CharField(max_length=200)
    explanation = models.TextField()
    examples = models.TextField()
    practice_exercises = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class AudioTask(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='audio_tasks')
    title = models.CharField(max_length=200)
    audio_url = models.URLField()
    transcript = models.TextField()
    questions = models.JSONField()  # Store questions and answers as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lesson.title} - {self.title}"

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_progress')
    completed = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    last_attempted = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"

    def mark_as_complete(self):
        self.completed = True
        self.score = 100 # Assuming 100 for completion, adjust if variable
        # last_attempted is auto_now=True, so it will be updated on save.
        # However, explicitly including it in update_fields is fine if we want to be very specific.
        self.save(update_fields=['completed', 'score', 'last_attempted'])

    def update_score(self, new_score):
        self.score = max(self.score, int(new_score)) # Ensures score doesn't decrease, and new_score is int
        # self.completed can be set here if a certain score means completion, e.g.
        # if self.score >= 100: # Assuming 100 is max score and means completion
        #     self.completed = True
        #     self.save(update_fields=['score', 'completed', 'last_attempted'])
        # else:
        #     self.save(update_fields=['score', 'last_attempted'])
        # For now, keeping it simple as per the prompt, only updating score.
        self.save(update_fields=['score', 'last_attempted'])

class PronunciationExercise(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='pronunciation_exercises')
    word = models.CharField(max_length=100)
    correct_pronunciation = models.CharField(max_length=100)  # IPA notation
    audio_url = models.URLField(blank=True)  # Reference audio
    difficulty = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.word} - {self.difficulty}"

class PronunciationAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exercise = models.ForeignKey(PronunciationExercise, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='pronunciation_attempts/')
    transcription = models.TextField(blank=True)
    accuracy_score = models.FloatField(null=True)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.exercise.word}"

class UserXP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='xp')
    total_xp = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Level {self.level}"

    def add_xp(self, amount, is_recursive_call=False):
        self.total_xp += amount
        new_level = (self.total_xp // 1000) + 1  # Calculate new level first

        level_up_occurred = False
        if new_level > self.level:
            level_up_occurred = True

        self.level = new_level
        # Removed self.save() here, will be called once after all modifications in this method.

        if not is_recursive_call:
            self.update_streak() # Call update_streak for primary XP gains.

        self.save() # Save after all modifications including level and streak.

        if not is_recursive_call:
            # Pass the flag indicating if a level up happened specifically in *this* call to add_xp
            self._check_achievements(level_up_occurred_during_this_add_xp=level_up_occurred)

    def _try_award_achievement(self, achievement_type, xp_reward):
        """
        Tries to award an achievement to the user.
        If the achievement is newly awarded, adds XP.
        """
        achievement, created = UserAchievement.objects.get_or_create(
            user=self.user,
            type=achievement_type,
            defaults={'xp_reward': xp_reward}
        )
        if created:
            # Call add_xp recursively, ensuring it doesn't trigger another achievement check cycle for this specific XP gain.
            self.add_xp(xp_reward, is_recursive_call=True)
            # One might also create a Notification here if achievements should notify users.
            # Notification.objects.create(user=self.user, type='ACHIEVEMENT', title=f"Achievement Unlocked: {achievement_type}", message=f"You earned {xp_reward} XP!")

    def _check_achievements(self, level_up_occurred_during_this_add_xp=False):
        """
        Checks and awards achievements based on user's XP, level, and streak.
        `level_up_occurred_during_this_add_xp` is True if a level up happened in the current add_xp call.
        """
        # Level up achievement
        # This specifically checks if the level up was due to the most recent XP gain.
        if level_up_occurred_during_this_add_xp:
            self._try_award_achievement('LEVEL_UP', 200) # XP reward for leveling up

        # Streak achievements
        # These are typically checked when streak is updated, but can also be checked here.
        # Ensure streak_days is up-to-date before these checks if called from places other than update_streak.
        if self.streak_days == 3:
            self._try_award_achievement('STREAK_3', 100)
        elif self.streak_days == 7:
            self._try_award_achievement('STREAK_7', 300)
        elif self.streak_days == 30: # As per the view logic
            self._try_award_achievement('STREAK_30', 1000)

        # Example: Perfect score achievement (if applicable, might need more context)
        # if some_condition_for_perfect_score:
        # self._try_award_achievement('PERFECT_SCORE', 50)

        # Example: Lesson complete achievement (usually triggered elsewhere, e.g., after a lesson is completed)
        # if number_of_lessons_completed == 1:
        # self._try_award_achievement('LESSON_COMPLETE', 50)


    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity_date is None or self.last_activity_date < today - timedelta(days=1):
            self.streak_days = 1  # Start or reset streak
        elif self.last_activity_date == today - timedelta(days=1):
            self.streak_days += 1 # Increment streak
        # If last_activity_date is today, streak_days should not change here.
        # It implies multiple activities in the same day.

        self.last_activity_date = today
        # Removed self.save() from here, it will be called in add_xp or if update_streak is called standalone.
        # If called standalone, the caller should handle saving, or add:
        # self.save(update_fields=['streak_days', 'last_activity_date'])

class UserAchievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('LESSON_COMPLETE', 'Complete a Lesson'),
        ('STREAK_3', '3 Day Streak'),
        ('STREAK_7', '7 Day Streak'),
        ('STREAK_30', '30 Day Streak'),
        ('PERFECT_SCORE', 'Perfect Score'),
        ('LEVEL_UP', 'Level Up'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    xp_reward = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'type']

    def __str__(self):
        return f"{self.user.username} - {self.type}"

class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    target_language = models.CharField(max_length=50)
    current_level = models.CharField(max_length=2, choices=Course.LEVEL_CHOICES)
    learning_goal = models.CharField(max_length=100)
    daily_goal_minutes = models.PositiveIntegerField(default=30)
    preferred_lesson_types = models.JSONField(default=list)  # List of preferred lesson types
    weak_areas = models.JSONField(default=list)  # List of topics user struggles with
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s preferences"

class LessonRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    score = models.FloatField()  # Recommendation score
    reason = models.CharField(max_length=200)  # Why this lesson was recommended
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'lesson']
        ordering = ['-score']

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.lesson.title}"

class NotificationPreference(models.Model):
    NOTIFICATION_TYPES = [
        ('DAILY_REMINDER', 'Daily Learning Reminder'),
        ('WORD_OF_DAY', 'Word of the Day'),
        ('PROGRESS_UPDATE', 'Progress Update'),
        ('STREAK_ALERT', 'Streak Alert'),
        ('ACHIEVEMENT', 'Achievement Unlocked'),
        ('RECOMMENDATION', 'New Lesson Recommendation'),
    ]

    CHANNEL_CHOICES = [
        ('EMAIL', 'Email'),
        ('PUSH', 'Push Notification'),
        ('BOTH', 'Both'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    push_enabled = models.BooleanField(default=True)
    notification_types = models.JSONField(default=dict)  # Maps notification type to channel
    preferred_time = models.TimeField(default='09:00')  # Default to 9 AM
    timezone = models.CharField(max_length=50, default='UTC')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s notification preferences"

class NotificationManager(models.Manager):
    def get_unread_for_user(self, user):
        return self.filter(user=user, read=False).order_by('-created_at') # Added ordering

    def get_unsent_for_user(self, user):
        return self.filter(user=user, sent=False).order_by('-created_at') # Added ordering

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=NotificationPreference.NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    data = models.JSONField(default=dict)  # Additional data for the notification
    read = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type}"

    objects = NotificationManager() # Add the custom manager

    def mark_as_read(self):
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])

    def mark_as_sent(self):
        if not self.sent:
            self.sent = True
            self.sent_at = timezone.now() # Ensure timezone is imported in models.py
            self.save(update_fields=['sent', 'sent_at'])

# Manager for WordOfTheDay
class WordOfTheDayManager(models.Manager):
    def get_today(self):
        # timezone.now().date() ensures we are comparing date objects
        return self.filter(date=timezone.now().date()).first()

class WordOfTheDay(models.Model):
    word = models.CharField(max_length=100)
    translation = models.CharField(max_length=200)
    example_sentence = models.TextField()
    difficulty_level = models.CharField(max_length=2, choices=Course.LEVEL_CHOICES)
    date = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.word} - {self.date}"

    objects = WordOfTheDayManager() # Add the custom manager