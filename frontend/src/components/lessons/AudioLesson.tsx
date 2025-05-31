import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: string;
}

interface AudioTask {
  id: number;
  title: string;
  audio_url: string;
  transcript: string;
  questions: Question[];
}

interface Lesson {
  id: number;
  title: string;
  description: string;
  audio_tasks: AudioTask[];
}

const AudioLesson: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<{ [key: string]: string }>({});
  const [showTranscript, setShowTranscript] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

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

  const handleAnswerChange = (questionId: string, answer: string) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const handleNext = () => {
    if (lesson && currentIndex < lesson.audio_tasks.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setShowTranscript(false);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
      setShowTranscript(false);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
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

  const currentTask = lesson.audio_tasks[currentIndex];

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold mb-6">{lesson.title}</h2>
        <p className="text-gray-600 mb-8">{lesson.description}</p>

        <div className="mb-8">
          <div className="text-center mb-4">
            <span className="text-sm text-gray-500">
              {currentIndex + 1} of {lesson.audio_tasks.length}
            </span>
          </div>

          <div className="space-y-6">
            <div>
              <h3 className="text-2xl font-bold mb-4">{currentTask.title}</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <audio
                  ref={audioRef}
                  controls
                  className="w-full"
                  src={currentTask.audio_url}
                >
                  Your browser does not support the audio element.
                </audio>
              </div>
            </div>

            <div>
              <button
                onClick={() => setShowTranscript(!showTranscript)}
                className="text-primary-600 hover:text-primary-700"
              >
                {showTranscript ? 'Hide Transcript' : 'Show Transcript'}
              </button>
              {showTranscript && (
                <div className="mt-4 bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700 whitespace-pre-line">
                    {currentTask.transcript}
                  </p>
                </div>
              )}
            </div>

            <div>
              <h4 className="text-xl font-semibold mb-3">Comprehension Questions</h4>
              <div className="space-y-4">
                {currentTask.questions.map((question) => (
                  <div key={question.id} className="bg-gray-50 rounded-lg p-4">
                    <p className="text-gray-700 mb-3">{question.question}</p>
                    <div className="space-y-2">
                      {question.options.map((option) => (
                        <label
                          key={option}
                          className="flex items-center space-x-2 cursor-pointer"
                        >
                          <input
                            type="radio"
                            name={question.id}
                            value={option}
                            checked={userAnswers[question.id] === option}
                            onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                            className="form-radio text-primary-600"
                          />
                          <span className="text-gray-700">{option}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
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
            disabled={currentIndex === lesson.audio_tasks.length - 1}
            className="px-4 py-2 bg-primary-600 text-white rounded-md disabled:opacity-50"
          >
            Next
          </button>
        </div>

        {currentIndex === lesson.audio_tasks.length - 1 && (
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

export default AudioLesson; 