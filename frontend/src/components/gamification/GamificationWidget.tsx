import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface UserProfile {
  xp_points: number;
  level: number;
  streak_count: number;
  daily_goal_minutes: number;
}

const GamificationWidget: React.FC = () => {
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
        setError('Failed to load gamification data.');
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  if (loading) return <div>Loading gamification...</div>;
  if (error) return <div>{error}</div>;
  if (!profile) return null;

  const xpForNextLevel = 1000;
  const xpProgress = (profile.xp_points % xpForNextLevel) / xpForNextLevel * 100;

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Your Progress</h2>
      <div className="mb-2">Level: <span className="font-semibold">{profile.level}</span></div>
      <div className="mb-2">XP: <span className="font-semibold">{profile.xp_points}</span></div>
      <div className="mb-2">Streak: <span className="font-semibold">{profile.streak_count} days</span></div>
      <div className="mb-2">Daily Goal: <span className="font-semibold">{profile.daily_goal_minutes} min</span></div>
      <div className="w-full bg-gray-200 rounded-full h-3 mt-2">
        <div
          className="bg-blue-500 h-3 rounded-full"
          style={{ width: `${xpProgress}%` }}
        ></div>
      </div>
      <div className="text-xs text-gray-500 mt-1">{xpForNextLevel - (profile.xp_points % xpForNextLevel)} XP to next level</div>
    </div>
  );
};

export default GamificationWidget; 