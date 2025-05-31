import React, { useEffect, useState } from 'react';
import axios from 'axios';

interface Achievement {
  id: number;
  name: string;
  description: string;
  type: string;
  date_earned: string;
}

const AchievementsList: React.FC = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAchievements = async () => {
      try {
        const token = localStorage.getItem('token');
        const res = await axios.get('/api/users/achievements/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setAchievements(res.data);
      } catch (err) {
        setError('Failed to load achievements.');
      } finally {
        setLoading(false);
      }
    };
    fetchAchievements();
  }, []);

  if (loading) return <div>Loading achievements...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Achievements</h2>
      {achievements.length === 0 ? (
        <div>No achievements yet.</div>
      ) : (
        <ul className="space-y-2">
          {achievements.map((ach) => (
            <li key={ach.id} className="border-b pb-2">
              <div className="font-semibold">{ach.name}</div>
              <div className="text-sm text-gray-600">{ach.description}</div>
              <div className="text-xs text-gray-400">Earned: {new Date(ach.date_earned).toLocaleDateString()}</div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AchievementsList; 