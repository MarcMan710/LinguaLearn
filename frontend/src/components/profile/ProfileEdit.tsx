import React, { useState, useEffect } from 'react';
import { get, put } from '../../utils/api';

interface ProfileData {
  username: string;
  email: string;
  target_language: string;
  current_level: string;
  learning_goal: string;
  daily_goal_minutes: number;
}

const LANGUAGE_OPTIONS = [
  { value: 'EN', label: 'English' },
  { value: 'ES', label: 'Spanish' },
  { value: 'FR', label: 'French' },
  { value: 'DE', label: 'German' },
  { value: 'IT', label: 'Italian' },
  { value: 'PT', label: 'Portuguese' },
  { value: 'RU', label: 'Russian' },
  { value: 'ZH', label: 'Chinese' },
  { value: 'JA', label: 'Japanese' },
  { value: 'KO', label: 'Korean' },
];

const LEVEL_OPTIONS = [
  { value: 'A1', label: 'Beginner' },
  { value: 'A2', label: 'Elementary' },
  { value: 'B1', label: 'Intermediate' },
  { value: 'B2', label: 'Upper Intermediate' },
  { value: 'C1', label: 'Advanced' },
  { value: 'C2', label: 'Mastery' },
];

const GOAL_OPTIONS = [
  { value: 'CASUAL', label: 'Casual Learning' },
  { value: 'TRAVEL', label: 'Travel' },
  { value: 'BUSINESS', label: 'Business' },
  { value: 'ACADEMIC', label: 'Academic' },
  { value: 'FLUENCY', label: 'Native-like Fluency' },
];

const ProfileEdit: React.FC = () => {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;

    try {
      await put('/users/profile/', profile);
      setSuccess('Profile updated successfully!');
      setIsEditing(false);
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to update profile.');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    if (!profile) return;
    const { name, value } = e.target;
    setProfile({ ...profile, [name]: value });
  };

  if (loading) return <div>Loading profile...</div>;
  if (!profile) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Edit Profile</h2>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {isEditing ? 'Cancel' : 'Edit Profile'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="mb-4 p-3 bg-green-100 text-green-700 rounded">
          {success}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={profile.username}
              onChange={handleChange}
              disabled={!isEditing}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={profile.email}
              onChange={handleChange}
              disabled={!isEditing}
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Language
            </label>
            <select
              name="target_language"
              value={profile.target_language}
              onChange={handleChange}
              disabled={!isEditing}
              className="w-full px-3 py-2 border rounded-md"
            >
              {LANGUAGE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Level
            </label>
            <select
              name="current_level"
              value={profile.current_level}
              onChange={handleChange}
              disabled={!isEditing}
              className="w-full px-3 py-2 border rounded-md"
            >
              {LEVEL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Learning Goal
            </label>
            <select
              name="learning_goal"
              value={profile.learning_goal}
              onChange={handleChange}
              disabled={!isEditing}
              className="w-full px-3 py-2 border rounded-md"
            >
              {GOAL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Daily Goal (minutes)
            </label>
            <input
              type="number"
              name="daily_goal_minutes"
              value={profile.daily_goal_minutes}
              onChange={handleChange}
              disabled={!isEditing}
              min="5"
              max="120"
              className="w-full px-3 py-2 border rounded-md"
            />
          </div>
        </div>

        {isEditing && (
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            >
              Save Changes
            </button>
          </div>
        )}
      </form>
    </div>
  );
};

export default ProfileEdit; 