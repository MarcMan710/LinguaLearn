import React, { useEffect, useState } from 'react';
import { get } from '../../utils/api';

interface DailyProgress {
  daily_goal_minutes: number;
  minutes_learned_today: number;
  lessons_completed_today: number;
  streak_count: number;
  next_goal: number;
}

const DailyProgress: React.FC = () => {
  const [progress, setProgress] = useState<DailyProgress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchDailyProgress = async () => {
      try {
        const res = await get('/users/progress/daily/');
        setProgress(res.data);
      } catch (err) {
        setError('Failed to load daily progress.');
      } finally {
        setLoading(false);
      }
    };
    fetchDailyProgress();
  }, []);

  if (loading) return <div>Loading daily progress...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!progress) return null;

  const progressPercentage = (progress.minutes_learned_today / progress.daily_goal_minutes) * 100;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Today's Progress</h2>
      
      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            {progress.minutes_learned_today} / {progress.daily_goal_minutes} minutes
          </span>
          <span className="text-sm font-medium text-gray-700">
            {Math.round(progressPercentage)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className="bg-blue-600 h-4 rounded-full transition-all duration-500"
            style={{ width: `${Math.min(progressPercentage, 100)}%` }}
          ></div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-blue-800">Lessons Completed</h3>
          <p className="text-2xl font-bold text-blue-600">
            {progress.lessons_completed_today}
          </p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-green-800">Current Streak</h3>
          <p className="text-2xl font-bold text-green-600">
            {progress.streak_count} days
          </p>
        </div>
      </div>

      {/* Next Goal */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700">Next Goal</h3>
        <p className="text-lg font-semibold text-gray-900">
          {progress.next_goal} minutes to maintain streak
        </p>
      </div>
    </div>
  );
};

export default DailyProgress; 