import React, { useState } from 'react';
import InteractiveExercise from './InteractiveExercise';

interface Question {
  id: number;
  question: string;
  options: string[];
  correctAnswer: number;
  explanation: string;
}

interface QuizProps {
  questions: Question[];
  onComplete: (score: number) => void;
  onNext: () => void;
}

const Quiz: React.FC<QuizProps> = ({ questions, onComplete, onNext }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [correctAnswers, setCorrectAnswers] = useState(0);

  const currentQuestion = questions[currentIndex];

  const handleAnswerSelect = (optionIndex: number) => {
    setSelectedAnswer(optionIndex);
    setShowExplanation(true);

    if (optionIndex === currentQuestion.correctAnswer) {
      setCorrectAnswers(correctAnswers + 1);
    }
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setSelectedAnswer(null);
      setShowExplanation(false);
    } else {
      const score = (correctAnswers / questions.length) * 100;
      onComplete(score);
    }
  };

  return (
    <InteractiveExercise
      type="quiz"
      title="Multiple Choice Quiz"
      description="Test your knowledge with multiple choice questions"
      onComplete={onComplete}
      onNext={onNext}
    >
      <div className="space-y-6">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">
            {currentQuestion.question}
          </h3>
          <div className="space-y-3">
            {currentQuestion.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswerSelect(index)}
                disabled={showExplanation}
                className={`w-full text-left p-4 rounded-lg transition-colors ${
                  selectedAnswer === index
                    ? index === currentQuestion.correctAnswer
                      ? 'bg-green-100 border-2 border-green-500'
                      : 'bg-red-100 border-2 border-red-500'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>

        {showExplanation && (
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-blue-800">{currentQuestion.explanation}</p>
            <button
              onClick={handleNext}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              {currentIndex < questions.length - 1 ? 'Next Question' : 'Finish Quiz'}
            </button>
          </div>
        )}
      </div>

      <div className="mt-4 text-center text-gray-600">
        Question {currentIndex + 1} of {questions.length}
      </div>
    </InteractiveExercise>
  );
};

export default Quiz; 