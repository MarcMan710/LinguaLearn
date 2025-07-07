import React, { useState, useEffect } from 'react';
import { get } from '../../utils/api';

interface Achievement {
  type: string;
  xp_reward: number;
  created_at: string;
}

interface UserXP {
  username: string;
  total_xp: number;
  level: number;
  streak_days: number;
  achievements: Achievement[];
}

const ACHIEVEMENT_INFO = {
  LESSON_COMPLETE: {
    title: 'Lesson Master',
    description: 'Complete a lesson',
    icon: '📚',
  },
  STREAK_3: {
    title: 'Getting Started',
    description: 'Maintain a 3-day streak',
    icon: '🔥',
  },
  STREAK_7: {
    title: 'Week Warrior',
    description: 'Maintain a 7-day streak',
    icon: '⚡',
  },
  STREAK_30: {
    title: 'Monthly Master',
    description: 'Maintain a 30-day streak',
    icon: '🌟',
  },
  PERFECT_SCORE: {
    title: 'Perfect Performance',
    description: 'Get a perfect score on any exercise',
    icon: '💯',
  },
  LEVEL_UP: {
    title: 'Level Up!',
    description: 'Reach a new level',
    icon: '⬆️',
  },
};

const Achievements: React.FC = () => {
  const [userXP, setUserXP] = useState<UserXP | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUserXP();
  }, []);

  const fetchUserXP = async () => {
    try {
      const response = await get('/user-xp/');
      setUserXP(response.data[0]);
      setError(null);
    } catch (err) {
      setError('Error loading achievements. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Achievements</h2>

        {loading ? (
          <div className="text-center py-4">Loading...</div>
        ) : error ? (
          <div className="text-center py-4 text-red-600">{error}</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {userXP?.achievements.map((achievement) => {
              const info = ACHIEVEMENT_INFO[achievement.type as keyof typeof ACHIEVEMENT_INFO];
              return (
                <div
                  key={achievement.type}
                  className="bg-blue-50 rounded-lg p-4 flex items-start space-x-4"
                >
                  <div className="text-4xl">{info.icon}</div>
                  <div>
                    <h3 className="font-semibold text-blue-800">{info.title}</h3>
                    <p className="text-sm text-blue-600 mb-2">{info.description}</p>
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>+{achievement.xp_reward} XP</span>
                      <span>Earned {formatDate(achievement.created_at)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {userXP && userXP.achievements.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No achievements yet. Keep learning to earn achievements!
          </div>
        )}
      </div>
    </div>
  );
};

export default Achievements; 