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

    def add_xp(self, amount):
        self.total_xp += amount
        # Level up logic: 1000 XP per level
        self.level = (self.total_xp // 1000) + 1
        self.save()

    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity_date < today - timedelta(days=1):
            self.streak_days = 1
        else:
            self.streak_days += 1
        self.last_activity_date = today
        self.save()

class UserAchievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('LESSON_COMPLETE', 'Complete a Lesson'),
        ('STREAK_3', '3 Day Streak'),
        ('STREAK_7', '7 Day Streak'),
        ('STREAK_30', '30 Day Streak'),
        ('PERFECT_SCORE', 'Perfect Score'),
        ('LEVEL_UP', 'Level Up'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_achievements')
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