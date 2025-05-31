import React, { useState } from 'react';
import InteractiveExercise from './InteractiveExercise';

interface Blank {
  id: number;
  correctAnswer: string;
  options: string[];
}

interface FillBlankProps {
  text: string;
  blanks: Blank[];
  onComplete: (score: number) => void;
  onNext: () => void;
}

const FillBlank: React.FC<FillBlankProps> = ({
  text,
  blanks,
  onComplete,
  onNext,
}) => {
  const [answers, setAnswers] = useState<string[]>(Array(blanks.length).fill(''));
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleAnswerChange = (index: number, value: string) => {
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = () => {
    setIsSubmitted(true);
    const correctAnswers = answers.filter(
      (answer, index) => answer.toLowerCase() === blanks[index].correctAnswer.toLowerCase()
    );
    const score = (correctAnswers.length / blanks.length) * 100;
    onComplete(score);
  };

  const renderText = () => {
    const parts = text.split('___');
    return parts.map((part, index) => (
      <React.Fragment key={index}>
        {part}
        {index < blanks.length && (
          <select
            value={answers[index]}
            onChange={(e) => handleAnswerChange(index, e.target.value)}
            disabled={isSubmitted}
            className={`mx-1 px-2 py-1 rounded border ${
              isSubmitted
                ? answers[index].toLowerCase() ===
                  blanks[index].correctAnswer.toLowerCase()
                  ? 'bg-green-100 border-green-500'
                  : 'bg-red-100 border-red-500'
                : 'bg-white border-gray-300'
            }`}
          >
            <option value="">Select...</option>
            {blanks[index].options.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        )}
      </React.Fragment>
    ));
  };

  return (
    <InteractiveExercise
      type="fillblank"
      title="Fill in the Blanks"
      description="Complete the text by selecting the correct words"
      onComplete={onComplete}
      onNext={onNext}
    >
      <div className="space-y-6">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <p className="text-lg text-gray-800 leading-relaxed">{renderText()}</p>
        </div>

        {isSubmitted && (
          <div className="bg-blue-50 rounded-lg p-4">
            <h4 className="font-semibold text-blue-800 mb-2">Explanation:</h4>
            <p className="text-blue-600">
              {answers.every(
                (answer, index) =>
                  answer.toLowerCase() === blanks[index].correctAnswer.toLowerCase()
              )
                ? 'Great job! All answers are correct.'
                : 'Some answers are incorrect. Review the correct answers and try again.'}
            </p>
          </div>
        )}

        {!isSubmitted && (
          <button
            onClick={handleSubmit}
            disabled={answers.some((answer) => answer === '')}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            Check Answers
          </button>
        )}
      </div>
    </InteractiveExercise>
  );
};

export default FillBlank; 