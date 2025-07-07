import React, { useEffect, useState } from 'react';
import { get } from '../../utils/api';
import { format, startOfWeek, addDays } from 'date-fns';

interface ProgressStats {
  total_lessons_completed: number;
  total_minutes_learned: number;
  current_streak: number;
  longest_streak: number;
  weekly_progress: {
    date: string;
    minutes_learned: number;
    lessons_completed: number;
  }[];
}

interface CompletedLesson {
  id: number;
  title: string;
  type: string;
  completed_at: string;
  score: number;
}

const ProgressDashboard: React.FC = () => {
  const [stats, setStats] = useState<ProgressStats | null>(null);
  const [recentLessons, setRecentLessons] = useState<CompletedLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const [statsRes, lessonsRes] = await Promise.all([
          get('/users/progress/stats/'),
          get('/users/progress/completed-lessons/'),
        ]);
        setStats(statsRes.data);
        setRecentLessons(lessonsRes.data);
      } catch (err) {
        setError('Failed to load progress data.');
      } finally {
        setLoading(false);
      }
    };
    fetchProgress();
  }, []);

  if (loading) return <div className="flex justify-center items-center min-h-screen">Loading progress...</div>;
  if (error) return <div className="text-red-500 text-center">{error}</div>;
  if (!stats) return null;

  // Generate week days for streak calendar
  const weekStart = startOfWeek(new Date());
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Overall Progress Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-700">Total Lessons</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.total_lessons_completed}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-700">Total Minutes</h3>
            <p className="text-3xl font-bold text-green-600">{stats.total_minutes_learned}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-700">Current Streak</h3>
            <p className="text-3xl font-bold text-orange-600">{stats.current_streak} days</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <h3 className="text-lg font-semibold text-gray-700">Longest Streak</h3>
            <p className="text-3xl font-bold text-purple-600">{stats.longest_streak} days</p>
          </div>
        </div>

        {/* Weekly Progress Calendar */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Weekly Progress</h2>
          <div className="grid grid-cols-7 gap-2">
            {weekDays.map((day) => {
              const dayProgress = stats.weekly_progress.find(
                (p) => p.date === format(day, 'yyyy-MM-dd')
              );
              return (
                <div
                  key={day.toString()}
                  className="text-center p-2 border rounded-lg"
                >
                  <div className="text-sm text-gray-600">
                    {format(day, 'EEE')}
                  </div>
                  <div className="text-sm font-semibold">
                    {dayProgress ? `${dayProgress.minutes_learned}m` : '0m'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {dayProgress ? `${dayProgress.lessons_completed} lessons` : '0 lessons'}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Completed Lessons */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">Recent Completed Lessons</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Lesson
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Completed
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentLessons.map((lesson) => (
                  <tr key={lesson.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {lesson.title}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{lesson.type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{lesson.score}%</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {format(new Date(lesson.completed_at), 'MMM d, yyyy')}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressDashboard; 