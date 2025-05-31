import React, { useEffect, useState } from 'react';
import axios from 'axios';
import GamificationWidget from './gamification/GamificationWidget';
import AchievementsList from './gamification/AchievementsList';
import ProgressDashboard from './progress/ProgressDashboard';
import DailyProgress from './progress/DailyProgress';

interface UserProfile {
  username: string;
  email: string;
  target_language: string;
  current_level: string;
  learning_goal: string;
  daily_goal_minutes: number;
}

const UserProfile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/users/profile/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setProfile(res.data);
      } catch (err) {
        setError('Failed to load profile data.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  if (loading) return <div className="flex justify-center items-center min-h-screen">Loading profile...</div>;
  if (error) return <div className="text-red-500 text-center">{error}</div>;
  if (!profile) return null;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Profile Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-2xl font-bold mb-4">Welcome, {profile.username}!</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-gray-600">Email: {profile.email}</p>
              <p className="text-gray-600">Target Language: {profile.target_language}</p>
            </div>
            <div>
              <p className="text-gray-600">Current Level: {profile.current_level}</p>
              <p className="text-gray-600">Learning Goal: {profile.learning_goal}</p>
            </div>
          </div>
        </div>

        {/* Daily Progress */}
        <div className="mb-6">
          <DailyProgress />
        </div>

        {/* Gamification Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <GamificationWidget />
          <AchievementsList />
        </div>

        {/* Progress Dashboard */}
        <div className="mb-6">
          <ProgressDashboard />
        </div>

        {/* Learning Stats */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Learning Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{profile.daily_goal_minutes}</div>
              <div className="text-gray-600">Daily Goal (minutes)</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{profile.current_level}</div>
              <div className="text-gray-600">Current Level</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{profile.target_language}</div>
              <div className="text-gray-600">Target Language</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile; 