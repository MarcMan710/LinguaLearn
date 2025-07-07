import React, { useState, useEffect } from 'react';
import { get } from '../../utils/api';

interface LeaderboardEntry {
  username: string;
  total_xp: number;
  level: number;
  streak_days: number;
  rank: number;
}

interface UserXP {
  username: string;
  total_xp: number;
  level: number;
  streak_days: number;
  achievements: {
    type: string;
    xp_reward: number;
    created_at: string;
  }[];
}

const Leaderboard: React.FC = () => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [userXP, setUserXP] = useState<UserXP | null>(null);
  const [showFriendsOnly, setShowFriendsOnly] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLeaderboard();
    fetchUserXP();
  }, [showFriendsOnly]);

  const fetchLeaderboard = async () => {
    try {
      const response = await get(`/leaderboard/?friends_only=${showFriendsOnly}`);
      setEntries(response.data);
      setError(null);
    } catch (err) {
      setError('Error loading leaderboard. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchUserXP = async () => {
    try {
      const response = await get('/user-xp/');
      setUserXP(response.data[0]);
    } catch (err) {
      console.error('Error fetching user XP:', err);
    }
  };

  const formatXP = (xp: number) => {
    return xp.toLocaleString();
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">
            {showFriendsOnly ? 'Friends Leaderboard' : 'Global Leaderboard'}
          </h2>
          <button
            onClick={() => setShowFriendsOnly(!showFriendsOnly)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {showFriendsOnly ? 'Show Global' : 'Show Friends'}
          </button>
        </div>

        {userXP && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">Your Progress</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Level</p>
                <p className="text-xl font-bold text-blue-600">{userXP.level}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total XP</p>
                <p className="text-xl font-bold text-blue-600">{formatXP(userXP.total_xp)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Streak</p>
                <p className="text-xl font-bold text-blue-600">{userXP.streak_days} days</p>
              </div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-4">Loading...</div>
        ) : error ? (
          <div className="text-center py-4 text-red-600">{error}</div>
        ) : (
          <div className="space-y-4">
            {entries.map((entry) => (
              <div
                key={entry.username}
                className={`p-4 rounded-lg ${
                  entry.username === userXP?.username
                    ? 'bg-blue-100 border-2 border-blue-500'
                    : 'bg-gray-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 flex items-center justify-center bg-gray-200 rounded-full">
                      {entry.rank}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800">{entry.username}</p>
                      <p className="text-sm text-gray-600">Level {entry.level}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-800">{formatXP(entry.total_xp)} XP</p>
                    <p className="text-sm text-gray-600">{entry.streak_days} day streak</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard; 