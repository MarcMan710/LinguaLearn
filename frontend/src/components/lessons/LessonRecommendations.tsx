import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface Lesson {
  id: number;
  title: string;
  description: string;
  type: string;
  duration_minutes: number;
  course: {
    title: string;
    level: string;
  };
}

interface Recommendation {
  lesson: Lesson;
  score: number;
  reason: string;
  created_at: string;
}

const LessonRecommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get('/api/recommendations/generate_recommendations/');
      setRecommendations(response.data);
      setError(null);
    } catch (err) {
      setError('Error loading recommendations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getLessonTypeIcon = (type: string) => {
    switch (type) {
      case 'VOCABULARY':
        return '📚';
      case 'GRAMMAR':
        return '📝';
      case 'LISTENING':
        return '🎧';
      default:
        return '📖';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800">Recommended Lessons</h2>
          <button
            onClick={fetchRecommendations}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Refresh Recommendations
          </button>
        </div>

        {loading ? (
          <div className="text-center py-4">Loading recommendations...</div>
        ) : error ? (
          <div className="text-center py-4 text-red-600">{error}</div>
        ) : recommendations.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            No recommendations available. Complete some lessons to get personalized recommendations!
          </div>
        ) : (
          <div className="space-y-4">
            {recommendations.map((recommendation) => (
              <div
                key={recommendation.lesson.id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-2xl">
                        {getLessonTypeIcon(recommendation.lesson.type)}
                      </span>
                      <h3 className="text-lg font-semibold text-gray-800">
                        {recommendation.lesson.title}
                      </h3>
                    </div>
                    <p className="text-gray-600 mb-2">{recommendation.lesson.description}</p>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{recommendation.lesson.course.title}</span>
                      <span>•</span>
                      <span>Level {recommendation.lesson.course.level}</span>
                      <span>•</span>
                      <span>{recommendation.lesson.duration_minutes} minutes</span>
                    </div>
                    <p className="mt-2 text-sm text-blue-600">{recommendation.reason}</p>
                  </div>
                  <Link
                    to={`/lessons/${recommendation.lesson.id}`}
                    className="ml-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Start Lesson
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default LessonRecommendations; 