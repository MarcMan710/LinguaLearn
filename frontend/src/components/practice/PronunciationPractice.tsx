import React, { useState, useRef, useEffect } from 'react';
import { post } from '../../utils/api';
import InteractiveExercise from './InteractiveExercise';

interface PronunciationExercise {
  id: number;
  word: string;
  correct_pronunciation: string;
  audio_url: string;
  difficulty: string;
}

interface PronunciationAttempt {
  id: number;
  transcription: string;
  accuracy_score: number;
  feedback: string;
}

interface PronunciationPracticeProps {
  exercise: PronunciationExercise;
  onComplete: (score: number) => void;
  onNext: () => void;
}

const PronunciationPractice: React.FC<PronunciationPracticeProps> = ({
  exercise,
  onComplete,
  onNext,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [attempt, setAttempt] = useState<PronunciationAttempt | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioBlob(audioBlob);
        const url = URL.createObjectURL(audioBlob);
        setAudioUrl(url);
      };

      mediaRecorder.start();
      setIsRecording(true);
      setError(null);
    } catch (err) {
      setError('Error accessing microphone. Please ensure you have granted permission.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleSubmit = async () => {
    if (!audioBlob) return;

    setIsProcessing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'recording.wav');
      formData.append('exercise_id', exercise.id.toString());

      const response = await post('/pronunciation-attempts/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setAttempt(response.data);
      onComplete(response.data.accuracy_score);
    } catch (err) {
      setError('Error processing your pronunciation. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const playReferenceAudio = () => {
    const audio = new Audio(exercise.audio_url);
    audio.play();
  };

  return (
    <InteractiveExercise
      type="pronunciation"
      title="Pronunciation Practice"
      description="Practice your pronunciation and get instant feedback"
      onComplete={onComplete}
      onNext={onNext}
    >
      <div className="space-y-6">
        <div className="bg-white rounded-lg p-6 shadow-sm">
          <h3 className="text-2xl font-bold text-gray-800 mb-4">
            {exercise.word}
          </h3>
          <p className="text-gray-600 mb-4">
            IPA: {exercise.correct_pronunciation}
          </p>
          <button
            onClick={playReferenceAudio}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Listen to Reference
          </button>
        </div>

        <div className="bg-gray-50 rounded-lg p-6">
          <div className="flex justify-center space-x-4 mb-4">
            <button
              onClick={isRecording ? stopRecording : startRecording}
              className={`px-6 py-3 rounded-full ${
                isRecording
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-blue-600 hover:bg-blue-700'
              } text-white`}
            >
              {isRecording ? 'Stop Recording' : 'Start Recording'}
            </button>
          </div>

          {audioUrl && (
            <div className="mt-4">
              <audio src={audioUrl} controls className="w-full" />
              <button
                onClick={handleSubmit}
                disabled={isProcessing}
                className="mt-4 w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:bg-gray-400"
              >
                {isProcessing ? 'Processing...' : 'Submit for Feedback'}
              </button>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-100 text-red-800 rounded">
              {error}
            </div>
          )}

          {attempt && (
            <div className="mt-6 space-y-4">
              <div className="p-4 bg-blue-50 rounded">
                <h4 className="font-semibold text-blue-800 mb-2">Your Transcription:</h4>
                <p className="text-blue-600">{attempt.transcription}</p>
              </div>
              <div className="p-4 bg-green-50 rounded">
                <h4 className="font-semibold text-green-800 mb-2">Feedback:</h4>
                <p className="text-green-600">{attempt.feedback}</p>
              </div>
              <div className="p-4 bg-purple-50 rounded">
                <h4 className="font-semibold text-purple-800 mb-2">Accuracy Score:</h4>
                <p className="text-purple-600">
                  {Math.round(attempt.accuracy_score * 100)}%
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </InteractiveExercise>
  );
};

export default PronunciationPractice; 