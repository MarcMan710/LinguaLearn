import React, { useState, useRef } from 'react';
import InteractiveExercise from './InteractiveExercise';

interface Word {
  id: number;
  text: string;
  type: 'word' | 'punctuation';
}

interface DragDropProps {
  sentence: Word[];
  correctOrder: number[];
  onComplete: (score: number) => void;
  onNext: () => void;
}

const DragDrop: React.FC<DragDropProps> = ({
  sentence,
  correctOrder,
  onComplete,
  onNext,
}) => {
  const [words, setWords] = useState<Word[]>(sentence);
  const [draggedWord, setDraggedWord] = useState<Word | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const dropZoneRef = useRef<HTMLDivElement>(null);

  const handleDragStart = (word: Word) => {
    setDraggedWord(word);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (!draggedWord) return;

    const newWords = [...words];
    const draggedIndex = newWords.findIndex((w) => w.id === draggedWord.id);
    const dropIndex = Array.from(dropZoneRef.current?.children || []).findIndex(
      (child) => child === e.target
    );

    if (draggedIndex !== -1 && dropIndex !== -1) {
      const [removed] = newWords.splice(draggedIndex, 1);
      newWords.splice(dropIndex, 0, removed);
      setWords(newWords);

      // Check if the order is correct
      const isOrderCorrect = newWords.every(
        (word, index) => word.id === correctOrder[index]
      );
      setIsCorrect(isOrderCorrect);

      if (isOrderCorrect) {
        setTimeout(() => {
          onComplete(100);
        }, 1000);
      }
    }
  };

  return (
    <InteractiveExercise
      type="dragdrop"
      title="Sentence Construction"
      description="Drag and drop words to form a correct sentence"
      onComplete={onComplete}
      onNext={onNext}
    >
      <div className="space-y-6">
        <div
          ref={dropZoneRef}
          className="min-h-[100px] bg-gray-50 rounded-lg p-4 flex flex-wrap gap-2"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          {words.map((word) => (
            <div
              key={word.id}
              draggable
              onDragStart={() => handleDragStart(word)}
              className={`px-3 py-2 rounded cursor-move ${
                word.type === 'punctuation'
                  ? 'bg-gray-200'
                  : 'bg-blue-100 hover:bg-blue-200'
              }`}
            >
              {word.text}
            </div>
          ))}
        </div>

        {isCorrect !== null && (
          <div
            className={`p-4 rounded-lg ${
              isCorrect ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}
          >
            {isCorrect
              ? 'Correct! The sentence is properly constructed.'
              : 'Not quite right. Try again!'}
          </div>
        )}
      </div>
    </InteractiveExercise>
  );
};

export default DragDrop; 