from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from unittest.mock import patch, MagicMock, mock_open, call, ANY
import openai # For mocking openai.APIError
import os
from datetime import date, timedelta

from .models import (
    Course, Lesson, PronunciationExercise, PronunciationAttempt,
    UserXP, UserAchievement, UserPreferences, UserProgress
)
from .services import PronunciationService, RecommendationService

# --- Helper Functions ---

def create_test_user(username="testuser", password="password"):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': f"{username}@example.com", 'first_name': 'Test', 'last_name': 'User'}
    )
    if created:
        user.set_password(password)
        user.save()
    return user

def create_course(title="Test Course", level="A1"):
    course, _ = Course.objects.get_or_create(title=title, defaults={'description': "Desc", 'level': level, 'image_url': 'http://example.com/image.png'})
    return course

def create_lesson(course, title="Test Lesson", order=1, lesson_type='VOCABULARY'):
    lesson, _ = Lesson.objects.get_or_create(
        course=course,
        title=title,
        defaults={
            'description': "Lesson description",
            'type': lesson_type,
            'order': order,
            'duration_minutes': 10
        }
    )
    return lesson

def create_pronunciation_exercise(lesson, word="hello", correct_pronunciation="həˈloʊ"):
    exercise, _ = PronunciationExercise.objects.get_or_create(
        lesson=lesson,
        word=word,
        defaults={'correct_pronunciation': correct_pronunciation, 'difficulty': 'beginner'}
    )
    return exercise

def create_pronunciation_attempt(user, exercise, audio_file_name="test_audio.wav"):
    # Create a dummy audio file for the attempt
    # In a real scenario, ensure settings.MEDIA_ROOT is configured for tests if files are actually saved.
    # For these tests, we often mock the file operations.
    if not os.path.exists(settings.MEDIA_ROOT):
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    audio_path = os.path.join(settings.MEDIA_ROOT, audio_file_name)
    with open(audio_path, 'wb') as f:
        f.write(b"dummy audio content") # Minimal content for a fake wav

    attempt = PronunciationAttempt.objects.create(
        user=user,
        exercise=exercise,
        audio_file=audio_path # Path relative to MEDIA_ROOT or absolute if settings configured
    )
    return attempt

def create_user_preferences(user, current_level="A1", target_language="English", learning_goal="Fluency", preferred_lesson_types=None, weak_areas=None):
    preferences, _ = UserPreferences.objects.get_or_create(
        user=user,
        defaults={
            'current_level': current_level,
            'target_language': target_language,
            'learning_goal': learning_goal,
            'preferred_lesson_types': preferred_lesson_types or ['VOCABULARY', 'GRAMMAR'],
            'weak_areas': weak_areas or ['Pronunciation']
        }
    )
    return preferences

def create_user_progress(user, lesson, completed=False, score=0):
    progress, _ = UserProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={'completed': completed, 'score': score}
    )
    return progress

# --- Test Classes ---

class PronunciationServiceTests(TestCase):
    def setUp(self):
        self.user = create_test_user(username="pron_test_user")
        self.course = create_course(title="Pron Course")
        self.lesson = create_lesson(self.course, title="Pron Lesson")
        self.exercise = create_pronunciation_exercise(self.lesson, word="example")

        # Create a dummy file for audio_file.path to exist
        # The content of the file doesn't matter as 'open' will be mocked for transcription.
        self.mock_audio_file_path = os.path.join(settings.MEDIA_ROOT, "test_pron_audio.wav")
        with open(self.mock_audio_file_path, 'wb') as f:
            f.write(b"dummy audio")

        self.attempt = PronunciationAttempt.objects.create(
            user=self.user,
            exercise=self.exercise,
            audio_file=self.mock_audio_file_path # Path that exists
        )
        self.service = PronunciationService()

        # Mock settings.OPENAI_API_KEY if service __init__ depends on it strictly at instantiation
        # and it's not set in test environment settings
        if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
             settings.OPENAI_API_KEY = "test_api_key_for_pronunciation_service"


    @patch('openai.Audio.transcribe')
    @patch('openai.ChatCompletion.create')
    @patch('builtins.open', new_callable=mock_open, read_data=b"dummy audio data")
    def test_process_pronunciation_attempt_success(self, mock_file_open, mock_chat_completion, mock_audio_transcribe):
        mock_audio_transcribe.return_value = {'text': 'example transcription'}
        mock_chat_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Great job!"))]
        )

        initial_save_count = self.attempt.save._mock_call_count if hasattr(self.attempt.save, '_mock_call_count') else 0

        # Mock save method on the specific attempt instance to track its calls
        self.attempt.save = MagicMock()

        self.service.process_pronunciation_attempt(self.attempt, language="en")

        self.assertEqual(self.attempt.transcription, 'example transcription')
        self.assertEqual(self.attempt.feedback, "Great job!")
        self.assertTrue(0 <= self.attempt.accuracy_score <= 1) # Placeholder check
        self.attempt.save.assert_called() # Check that save was called on the instance

        mock_file_open.assert_called_once_with(self.mock_audio_file_path, 'rb')


    @patch('openai.Audio.transcribe', side_effect=openai.APIError("OpenAI API Error", http_status=500, request=None))
    @patch('builtins.open', new_callable=mock_open, read_data=b"dummy audio data")
    def test_process_pronunciation_attempt_openai_api_error(self, mock_file_open, mock_audio_transcribe):
        self.attempt.save = MagicMock()
        self.service.process_pronunciation_attempt(self.attempt, language="en")

        self.assertIn("OpenAI API Error", self.attempt.feedback)
        self.assertEqual(self.attempt.accuracy_score, 0.0)
        self.attempt.save.assert_called()
        mock_file_open.assert_called_once_with(self.mock_audio_file_path, 'rb')


    @patch('builtins.open', side_effect=FileNotFoundError("File not found"))
    def test_process_pronunciation_attempt_file_not_found(self, mock_file_open):
        # This test assumes that if audio_file.path is invalid, 'open' will raise FileNotFoundError.
        # The PronunciationService itself checks for audio_file.path validity first.
        # To truly test this part of the service, we might need to make audio_file.path None or invalid

        self.attempt.audio_file.path = "/invalid/path/to/audio.wav" # Ensure path is invalid for open
        self.attempt.save = MagicMock()

        self.service.process_pronunciation_attempt(self.attempt, language="en")

        # The service's initial check for path validity should handle this
        self.assertIn("Audio file not found at path: /invalid/path/to/audio.wav", self.attempt.feedback)
        self.assertEqual(self.attempt.accuracy_score, 0.0)
        self.attempt.save.assert_called()
        # mock_file_open should not be called if the path check fails first
        mock_file_open.assert_not_called()

    def tearDown(self):
        # Clean up the dummy audio file
        if os.path.exists(self.mock_audio_file_path):
            os.remove(self.mock_audio_file_path)

        # Attempt to clean up any other files created in MEDIA_ROOT for attempts
        # This is a bit broad, ideally scope cleanup to files created by these tests.
        for item_name in os.listdir(settings.MEDIA_ROOT):
            item_path = os.path.join(settings.MEDIA_ROOT, item_name)
            if os.path.isfile(item_path) and ("test_audio.wav" in item_name or "test_pron_audio.wav" in item_name) :
                try:
                    os.remove(item_path)
                except OSError:
                    pass # File might be locked or already deleted
        if os.path.exists(settings.MEDIA_ROOT) and not os.listdir(settings.MEDIA_ROOT):
             try:
                os.rmdir(settings.MEDIA_ROOT) # remove dir only if empty
             except OSError:
                pass


class RecommendationServiceTests(TestCase):
    def setUp(self):
        self.user = create_test_user(username="rec_test_user")
        self.course_a1 = create_course(title="A1 Course", level="A1")
        self.course_b1 = create_course(title="B1 Course", level="B1")

        self.lesson1_a1_voc = create_lesson(self.course_a1, title="A1 Vocab Intro", order=1, lesson_type="VOCABULARY")
        self.lesson2_a1_gram = create_lesson(self.course_a1, title="A1 Grammar Basics", order=2, lesson_type="GRAMMAR")
        self.lesson3_b1_list = create_lesson(self.course_b1, title="B1 Listening Practice", order=1, lesson_type="LISTENING")
        self.lesson4_a1_adv_voc = create_lesson(self.course_a1, title="A1 Advanced Vocab", order=3, lesson_type="VOCABULARY")
        self.lesson4_a1_adv_voc.description = "This lesson helps with English fluency." # For learning_goal test

        self.preferences = create_user_preferences(
            self.user,
            current_level="A1",
            preferred_lesson_types=["VOCABULARY", "LISTENING"],
            weak_areas=["Grammar", "Basics"], # For lesson2_a1_gram
            learning_goal="Fluency" # For lesson4_a1_adv_voc
        )

        # User has completed lesson1_a1_voc
        create_user_progress(self.user, self.lesson1_a1_voc, completed=True, score=100)
        self.user_progress_qs = UserProgress.objects.filter(user=self.user)

        self.service = RecommendationService()

    def test_calculate_lesson_score_high_match(self):
        # lesson2_a1_gram: Matches level (A1), weak area ("Grammar", "Basics"), builds on progress (order 2 > 1 completed)
        # Expected scores: Level=+2, WeakArea=+2, Progress=+1 = 5.0
        score, reason = self.service.calculate_lesson_score(self.lesson2_a1_gram, self.preferences, self.user_progress_qs)
        self.assertAlmostEqual(score, 5.0)
        self.assertIn("Matches your current level", reason)
        self.assertIn("Helps improve your weak areas", reason)
        self.assertIn("Builds upon your completed lessons", reason)

    def test_calculate_lesson_score_partial_match_type_and_goal(self):
        # lesson4_a1_adv_voc: Matches level (A1), preferred type (VOCABULARY), learning goal ("Fluency"), builds on progress
        # Expected: Level=+2, Type=+1.5, Goal=+1.5, Progress=+1 = 6.0
        self.lesson4_a1_adv_voc.save() # ensure description is saved
        score, reason = self.service.calculate_lesson_score(self.lesson4_a1_adv_voc, self.preferences, self.user_progress_qs)
        self.assertAlmostEqual(score, 6.0)
        self.assertIn("Matches your current level", reason)
        self.assertIn("Matches your preferred learning style", reason)
        self.assertIn("Aligns with your learning goal", reason)
        self.assertIn("Builds upon your completed lessons", reason)

    def test_calculate_lesson_score_no_match(self):
        # lesson3_b1_list: Different level (B1), but matches preferred type (LISTENING)
        # Expected: Type=+1.5 (No level match, no weak area, no progress build for different course level logic, no goal)
        score, reason = self.service.calculate_lesson_score(self.lesson3_b1_list, self.preferences, self.user_progress_qs)
        self.assertAlmostEqual(score, 1.5)
        self.assertIn("Matches your preferred learning style", reason)
        self.assertNotIn("Matches your current level", reason)


    def test_calculate_lesson_score_edge_cases_empty_prefs(self):
        self.preferences.preferred_lesson_types = []
        self.preferences.weak_areas = []
        self.preferences.learning_goal = ""
        self.preferences.save()
        # lesson2_a1_gram: Matches level (A1), builds on progress
        # Expected: Level=+2, Progress=+1 = 3.0
        score, reason = self.service.calculate_lesson_score(self.lesson2_a1_gram, self.preferences, self.user_progress_qs)
        self.assertAlmostEqual(score, 3.0)
        self.assertIn("Matches your current level", reason)
        self.assertIn("Builds upon your completed lessons", reason)
        self.assertNotIn("preferred learning style", reason)
        self.assertNotIn("weak areas", reason)
        self.assertNotIn("learning goal", reason)

    def test_calculate_lesson_score_no_progress_made(self):
        empty_progress = UserProgress.objects.none()
        # lesson2_a1_gram: Matches level (A1), weak area. No progress to build upon.
        # Expected: Level=+2, WeakArea=+2 = 4.0
        score, reason = self.service.calculate_lesson_score(self.lesson2_a1_gram, self.preferences, empty_progress)
        self.assertAlmostEqual(score, 4.0)
        self.assertIn("Matches your current level", reason)
        self.assertIn("Helps improve your weak areas", reason)
        self.assertNotIn("Builds upon your completed lessons", reason)


class UserXPModelTests(TestCase):
    def setUp(self):
        self.user = create_test_user(username="xp_test_user")
        self.user_xp, _ = UserXP.objects.get_or_create(user=self.user)

    def test_add_xp_level_up_awards_achievement(self):
        initial_xp = self.user_xp.total_xp
        initial_level = self.user_xp.level
        xp_to_add = 1000 - (initial_xp % 1000) + 50 # XP to ensure level up + 50 more

        self.user_xp.add_xp(xp_to_add)
        self.user_xp.refresh_from_db()

        self.assertEqual(self.user_xp.level, initial_level + 1)
        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='LEVEL_UP').exists())

        level_up_achievement = UserAchievement.objects.get(user=self.user, type='LEVEL_UP')
        expected_total_xp = initial_xp + xp_to_add + level_up_achievement.xp_reward
        self.assertEqual(self.user_xp.total_xp, expected_total_xp)

    def test_streak_achievements(self):
        # Test STREAK_3
        self.user_xp.streak_days = 3
        self.user_xp.save()
        # Add any amount of XP to trigger _check_achievements via non-recursive call
        self.user_xp.add_xp(10)
        self.user_xp.refresh_from_db()
        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='STREAK_3').exists())
        streak_3_ach = UserAchievement.objects.get(user=self.user, type='STREAK_3')
        # XP should be 10 (base) + 100 (streak_3 reward)
        self.assertEqual(self.user_xp.total_xp, 10 + streak_3_ach.xp_reward)

        # Reset for STREAK_7 (clear previous achievements and XP for isolated test)
        UserAchievement.objects.all().delete()
        self.user_xp.total_xp = 0; self.user_xp.level = 1; self.user_xp.save()
        self.user_xp.streak_days = 7
        self.user_xp.save()
        self.user_xp.add_xp(10)
        self.user_xp.refresh_from_db()
        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='STREAK_7').exists())
        streak_7_ach = UserAchievement.objects.get(user=self.user, type='STREAK_7')
        self.assertEqual(self.user_xp.total_xp, 10 + streak_7_ach.xp_reward)

        # Reset for STREAK_30
        UserAchievement.objects.all().delete()
        self.user_xp.total_xp = 0; self.user_xp.level = 1; self.user_xp.save()
        self.user_xp.streak_days = 30
        self.user_xp.save()
        self.user_xp.add_xp(10)
        self.user_xp.refresh_from_db()
        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='STREAK_30').exists())
        streak_30_ach = UserAchievement.objects.get(user=self.user, type='STREAK_30')
        self.assertEqual(self.user_xp.total_xp, 10 + streak_30_ach.xp_reward)


    def test_add_xp_no_achievement(self):
        initial_ach_count = UserAchievement.objects.count()
        self.user_xp.add_xp(50) # Assuming 50 XP doesn't trigger level up or streak
        self.user_xp.refresh_from_db()
        self.assertEqual(UserAchievement.objects.count(), initial_ach_count)
        self.assertEqual(self.user_xp.total_xp, 50)

    def test_recursive_call_prevention_on_achievement_xp(self):
        # Set conditions for a level up that will award 200 XP
        self.user_xp.total_xp = 900 # 100 XP away from level 2
        self.user_xp.level = 1
        self.user_xp.save()

        # Adding 150 XP will cause level up (to level 2), awarding 200 XP.
        # Total XP should be 900 (initial) + 150 (added) + 200 (LEVEL_UP achievement) = 1250.
        # The 200 XP from LEVEL_UP should not trigger _check_achievements again.
        # If it did, and say, streak conditions were met, it might award streak XP again.

        # For this test, let's also set streak_days to 3 to see if LEVEL_UP's XP re-triggers STREAK_3.
        self.user_xp.streak_days = 3
        self.user_xp.save()

        self.user_xp.add_xp(150) # This will trigger LEVEL_UP (200XP) and STREAK_3 (100XP) from the base 150XP.
        self.user_xp.refresh_from_db()

        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='LEVEL_UP').exists())
        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='STREAK_3').exists())

        level_up_xp = UserAchievement.objects.get(user=self.user, type='LEVEL_UP').xp_reward # 200
        streak_3_xp = UserAchievement.objects.get(user=self.user, type='STREAK_3').xp_reward # 100

        expected_xp = 900 + 150 + level_up_xp + streak_3_xp # 900+150+200+100 = 1350
        self.assertEqual(self.user_xp.total_xp, expected_xp)

        # Ensure only one of each achievement was created.
        self.assertEqual(UserAchievement.objects.filter(user=self.user, type='LEVEL_UP').count(), 1)
        self.assertEqual(UserAchievement.objects.filter(user=self.user, type='STREAK_3').count(), 1)


    def test_try_award_achievement_idempotency(self):
        initial_xp = self.user_xp.total_xp

        # First call: awards achievement and XP
        self.user_xp._try_award_achievement('TEST_ACH', 50)
        self.user_xp.refresh_from_db()
        self.assertTrue(UserAchievement.objects.filter(user=self.user, type='TEST_ACH').exists())
        self.assertEqual(self.user_xp.total_xp, initial_xp + 50)

        # Second call: should do nothing
        ach_count_before_second_call = UserAchievement.objects.count()
        xp_before_second_call = self.user_xp.total_xp

        self.user_xp._try_award_achievement('TEST_ACH', 50)
        self.user_xp.refresh_from_db()

        self.assertEqual(UserAchievement.objects.count(), ach_count_before_second_call) # No new achievement
        self.assertEqual(self.user_xp.total_xp, xp_before_second_call) # No new XP
```
