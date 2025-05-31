import React, { useState } from 'react';

interface ExerciseProps {
  type: 'flashcard' | 'quiz' | 'dragdrop' | 'fillblank';
  title: string;
  description: string;
  onComplete: (score: number) => void;
  onNext: () => void;
}

const InteractiveExercise: React.FC<ExerciseProps> = ({
  type,
  title,
  description,
  onComplete,
  onNext,
  children,
}) => {
  const [isCompleted, setIsCompleted] = useState(false);
  const [score, setScore] = useState(0);

  const handleComplete = (finalScore: number) => {
    setScore(finalScore);
    setIsCompleted(true);
    onComplete(finalScore);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-800">{title}</h2>
        <p className="text-gray-600 mt-2">{description}</p>
      </div>

      <div className="mb-6">
        {children}
      </div>

      {isCompleted && (
        <div className="mt-6 p-4 bg-green-50 rounded-lg">
          <div className="text-center">
            <p className="text-lg font-semibold text-green-800">
              Exercise Completed!
            </p>
            <p className="text-green-600 mt-2">Score: {score}%</p>
            <button
              onClick={onNext}
              className="mt-4 px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Next Exercise
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveExercise; 