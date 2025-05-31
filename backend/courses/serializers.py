from rest_framework import serializers
from .models import Course, Lesson, VocabularyItem, GrammarRule, AudioTask, UserProgress, PronunciationExercise, PronunciationAttempt, UserAchievement, UserXP, UserPreferences, LessonRecommendation, NotificationPreference, Notification, WordOfTheDay

class VocabularyItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyItem
        fields = '__all__'

class GrammarRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarRule
        fields = '__all__'

class AudioTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioTask
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    vocabulary_items = VocabularyItemSerializer(many=True, read_only=True)
    grammar_rules = GrammarRuleSerializer(many=True, read_only=True)
    audio_tasks = AudioTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

class UserProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    course_title = serializers.CharField(source='lesson.course.title', read_only=True)

    class Meta:
        model = UserProgress
        fields = ['id', 'lesson', 'lesson_title', 'course_title', 'completed', 'score', 'last_attempted']
        read_only_fields = ['last_attempted']

class PronunciationExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PronunciationExercise
        fields = ['id', 'word', 'correct_pronunciation', 'audio_url', 'difficulty']

class PronunciationAttemptSerializer(serializers.ModelSerializer):
    exercise = PronunciationExerciseSerializer(read_only=True)
    exercise_id = serializers.PrimaryKeyRelatedField(
        queryset=PronunciationExercise.objects.all(),
        write_only=True,
        source='exercise'
    )

    class Meta:
        model = PronunciationAttempt
        fields = ['id', 'exercise', 'exercise_id', 'audio_file', 'transcription', 
                 'accuracy_score', 'feedback', 'created_at']
        read_only_fields = ['transcription', 'accuracy_score', 'feedback']

class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievement
        fields = ['type', 'xp_reward', 'created_at']

class UserXPSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    achievements = UserAchievementSerializer(many=True, read_only=True)

    class Meta:
        model = UserXP
        fields = ['username', 'total_xp', 'level', 'streak_days', 'achievements']

class LeaderboardEntrySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    rank = serializers.SerializerMethodField()

    class Meta:
        model = UserXP
        fields = ['username', 'total_xp', 'level', 'streak_days', 'rank']

    def get_rank(self, obj):
        # Get the rank based on total_xp
        return UserXP.objects.filter(total_xp__gt=obj.total_xp).count() + 1

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = ['target_language', 'current_level', 'learning_goal', 
                 'daily_goal_minutes', 'preferred_lesson_types', 'weak_areas']
        read_only_fields = ['created_at', 'updated_at']

class LessonRecommendationSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)
    
    class Meta:
        model = LessonRecommendation
        fields = ['lesson', 'score', 'reason', 'created_at']
        read_only_fields = ['score', 'reason', 'created_at']

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['email_enabled', 'push_enabled', 'notification_types', 
                 'preferred_time', 'timezone']
        read_only_fields = ['created_at', 'updated_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'type', 'title', 'message', 'data', 'read', 
                 'sent', 'created_at', 'sent_at']
        read_only_fields = ['sent', 'sent_at']

class WordOfTheDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WordOfTheDay
        fields = ['word', 'translation', 'example_sentence', 
                 'difficulty_level', 'date'] 