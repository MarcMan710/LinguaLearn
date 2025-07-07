import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { get } from '../../utils/api';

interface Lesson {
  id: number;
  title: string;
  description: string;
  type: 'VOCABULARY' | 'GRAMMAR' | 'LISTENING';
  order: number;
  duration_minutes: number;
}

const LessonList: React.FC = () => {
  const { courseId } = useParams<{ courseId: string }>();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLessons = async () => {
      try {
        const response = await get(
          `/courses/${courseId}/lessons/`
        );
        setLessons(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load lessons');
        setLoading(false);
      }
    };

    fetchLessons();
  }, [courseId]);

  if (loading) return <div>Loading lessons...</div>;
  if (error) return <div className="text-red-500">{error}</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 className="text-2xl font-bold mb-6">Course Lessons</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {lessons.map((lesson) => (
          <div
            key={lesson.id}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                  {lesson.type}
                </span>
                <span className="text-sm text-gray-500">
                  {lesson.duration_minutes} min
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2">{lesson.title}</h3>
              <p className="text-gray-600 mb-4">{lesson.description}</p>
              <button
                onClick={() => window.location.href = `/lessons/${lesson.id}`}
                className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition-colors duration-300"
              >
                Start Lesson
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LessonList; 