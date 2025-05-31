import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface VocabularyItem {
  id: number;
  word: string;
  translation: string;
  example_sentence: string;
  pronunciation: string;
}

interface Lesson {
  id: number;
  title: string;
  description: string;
  vocabulary_items: VocabularyItem[];
}

const VocabularyLesson: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showTranslation, setShowTranslation] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLesson = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(
          `http://localhost:8000/api/lessons/${lessonId}/`,
          {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
        setLesson(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load lesson');
        setLoading(false);
      }
    };

    fetchLesson();
  }, [lessonId]);

  const handleNext = () => {
    if (lesson && currentIndex < lesson.vocabulary_items.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowTranslation(false);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowTranslation(false);
    }
  };

  const handleComplete = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:8000/api/lessons/${lessonId}/complete/`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      // Handle completion (e.g., show success message, redirect)
    } catch (err) {
      setError('Failed to mark lesson as complete');
    }
  };

  if (loading) return <div>Loading lesson...</div>;
  if (error) return <div className="text-red-500">{error}</div>;
  if (!lesson) return <div>Lesson not found</div>;

  const currentItem = lesson.vocabulary_items[currentIndex];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold mb-6">{lesson.title}</h2>
        <p className="text-gray-600 mb-8">{lesson.description}</p>

        <div className="mb-8">
          <div className="text-center mb-4">
            <span className="text-sm text-gray-500">
              {currentIndex + 1} of {lesson.vocabulary_items.length}
            </span>
          </div>

          <div
            className="bg-gray-50 rounded-lg p-8 cursor-pointer"
            onClick={() => setShowTranslation(!showTranslation)}
          >
            <h3 className="text-2xl font-bold mb-4 text-center">
              {currentItem.word}
            </h3>
            {showTranslation && (
              <div className="space-y-4">
                <p className="text-lg text-gray-700">
                  <span className="font-semibold">Translation:</span>{' '}
                  {currentItem.translation}
                </p>
                <p className="text-lg text-gray-700">
                  <span className="font-semibold">Pronunciation:</span>{' '}
                  {currentItem.pronunciation}
                </p>
                <p className="text-lg text-gray-700">
                  <span className="font-semibold">Example:</span>{' '}
                  {currentItem.example_sentence}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md disabled:opacity-50"
          >
            Previous
          </button>
          <button
            onClick={handleNext}
            disabled={currentIndex === lesson.vocabulary_items.length - 1}
            className="px-4 py-2 bg-primary-600 text-white rounded-md disabled:opacity-50"
          >
            Next
          </button>
        </div>

        {currentIndex === lesson.vocabulary_items.length - 1 && (
          <div className="mt-8 text-center">
            <button
              onClick={handleComplete}
              className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              Complete Lesson
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default VocabularyLesson; 