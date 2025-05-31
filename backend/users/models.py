from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('ES', 'Spanish'),
        ('FR', 'French'),
        ('DE', 'German'),
        ('IT', 'Italian'),
        ('PT', 'Portuguese'),
        ('RU', 'Russian'),
        ('ZH', 'Chinese'),
        ('JA', 'Japanese'),
        ('KO', 'Korean'),
    ]

    LEVEL_CHOICES = [
        ('A1', 'Beginner'),
        ('A2', 'Elementary'),
        ('B1', 'Intermediate'),
        ('B2', 'Upper Intermediate'),
        ('C1', 'Advanced'),
        ('C2', 'Mastery'),
    ]

    GOAL_CHOICES = [
        ('CASUAL', 'Casual Learning'),
        ('TRAVEL', 'Travel'),
        ('BUSINESS', 'Business'),
        ('ACADEMIC', 'Academic'),
        ('FLUENCY', 'Native-like Fluency'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    target_language = models.CharField(max_length=50)
    current_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1')
    learning_goal = models.TextField()
    daily_goal_minutes = models.PositiveIntegerField(default=15)
    
    # Gamification fields
    xp_points = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    streak_count = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(default=timezone.now)
    total_lessons_completed = models.PositiveIntegerField(default=0)
    total_minutes_learned = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def add_xp(self, points):
        self.xp_points += points
        self.update_level()
        self.save()
    
    def update_level(self):
        # Level up every 1000 XP points
        self.level = (self.xp_points // 1000) + 1
    
    def update_streak(self):
        today = timezone.now().date()
        if self.last_activity_date == today - timezone.timedelta(days=1):
            self.streak_count += 1
        elif self.last_activity_date < today - timezone.timedelta(days=1):
            self.streak_count = 1
        self.last_activity_date = today
        self.save()

class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('STREAK', 'Streak Achievement'),
        ('LESSONS', 'Lessons Completed'),
        ('MINUTES', 'Minutes Learned'),
        ('LEVEL', 'Level Up'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=10, choices=ACHIEVEMENT_TYPES)
    requirement = models.PositiveIntegerField()  # Number required to unlock
    xp_reward = models.PositiveIntegerField()
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}" 