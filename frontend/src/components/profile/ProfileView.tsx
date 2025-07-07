import React, { useState, useEffect } from 'react';
import { get } from '../../utils/api';
import { Link } from 'react-router-dom';

interface ProfileData {
  username: string;
  email: string;
  target_language: string;
  current_level: string;
  learning_goal: string;
  daily_goal_minutes: number;
  created_at: string;
}

const LANGUAGE_LABELS: { [key: string]: string } = {
  EN: 'English',
  ES: 'Spanish',
  FR: 'French',
  DE: 'German',
  IT: 'Italian',
  PT: 'Portuguese',
  RU: 'Russian',
  ZH: 'Chinese',
  JA: 'Japanese',
  KO: 'Korean',
};

const LEVEL_LABELS: { [key: string]: string } = {
  A1: 'Beginner',
  A2: 'Elementary',
  B1: 'Intermediate',
  B2: 'Upper Intermediate',
  C1: 'Advanced',
  C2: 'Mastery',
};

const GOAL_LABELS: { [key: string]: string } = {
  CASUAL: 'Casual Learning',
  TRAVEL: 'Travel',
  BUSINESS: 'Business',
  ACADEMIC: 'Academic',
  FLUENCY: 'Native-like Fluency',
};

const ProfileView: React.FC = () => {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const res = await get('/users/profile/');
      setProfile(res.data);
    } catch (err) {
      setError('Failed to load profile data.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading profile...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!profile) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Profile Information</h2>
        <Link
          to="/profile/edit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Edit Profile
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Username</h3>
            <p className="mt-1 text-lg">{profile.username}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Email</h3>
            <p className="mt-1 text-lg">{profile.email}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Member Since</h3>
            <p className="mt-1 text-lg">
              {new Date(profile.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-sm font-medium text-gray-500">Target Language</h3>
            <p className="mt-1 text-lg">{LANGUAGE_LABELS[profile.target_language]}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Current Level</h3>
            <p className="mt-1 text-lg">{LEVEL_LABELS[profile.current_level]}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Learning Goal</h3>
            <p className="mt-1 text-lg">{GOAL_LABELS[profile.learning_goal]}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-500">Daily Goal</h3>
            <p className="mt-1 text-lg">{profile.daily_goal_minutes} minutes</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileView; 