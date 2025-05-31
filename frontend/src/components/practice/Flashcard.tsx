import React, { useState } from 'react';
import InteractiveExercise from './InteractiveExercise';

interface FlashcardData {
  id: number;
  word: string;
  translation: string;
  example: string;
  pronunciation: string;
}

interface FlashcardProps {
  cards: FlashcardData[];
  onComplete: (score: number) => void;
  onNext: () => void;
}

const Flashcard: React.FC<FlashcardProps> = ({ cards, onComplete, onNext }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [correctAnswers, setCorrectAnswers] = useState(0);

  const currentCard = cards[currentIndex];

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleNext = () => {
    if (currentIndex < cards.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    } else {
      const score = (correctAnswers / cards.length) * 100;
      onComplete(score);
    }
  };

  const handleCorrect = () => {
    setCorrectAnswers(correctAnswers + 1);
    handleNext();
  };

  return (
    <InteractiveExercise
      type="flashcard"
      title="Vocabulary Flashcards"
      description="Practice vocabulary with interactive flashcards"
      onComplete={onComplete}
      onNext={onNext}
    >
      <div className="relative h-64 perspective-1000">
        <div
          className={`w-full h-full transition-transform duration-500 transform-style-3d ${
            isFlipped ? 'rotate-y-180' : ''
          }`}
        >
          {/* Front of card */}
          <div
            className={`absolute w-full h-full backface-hidden ${
              isFlipped ? 'hidden' : 'block'
            }`}
          >
            <div className="bg-blue-50 rounded-lg p-6 h-full flex flex-col justify-center items-center">
              <h3 className="text-2xl font-bold text-blue-800 mb-4">
                {currentCard.word}
              </h3>
              <p className="text-blue-600 mb-4">{currentCard.pronunciation}</p>
              <button
                onClick={handleFlip}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Show Translation
              </button>
            </div>
          </div>

          {/* Back of card */}
          <div
            className={`absolute w-full h-full backface-hidden rotate-y-180 ${
              isFlipped ? 'block' : 'hidden'
            }`}
          >
            <div className="bg-green-50 rounded-lg p-6 h-full flex flex-col justify-center items-center">
              <h3 className="text-2xl font-bold text-green-800 mb-4">
                {currentCard.translation}
              </h3>
              <p className="text-green-600 mb-4 italic">{currentCard.example}</p>
              <div className="flex space-x-4">
                <button
                  onClick={handleCorrect}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                >
                  I Knew It
                </button>
                <button
                  onClick={handleFlip}
                  className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
                >
                  Flip Back
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-4 text-center text-gray-600">
        Card {currentIndex + 1} of {cards.length}
      </div>
    </InteractiveExercise>
  );
};

export default Flashcard; 