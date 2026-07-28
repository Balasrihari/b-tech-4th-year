import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { quizzesService } from '../services/quizzes';
import { Plus, Play, Clock, Award, List } from 'lucide-react';

export default function QuizManager() {
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [quizMode, setQuizMode] = useState('list'); // list, taking, results
  const [answers, setAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const queryClient = useQueryClient();

  const { data: quizzes, isLoading } = useQuery({
    queryKey: ['quizzes'],
    queryFn: quizzesService.getAll,
    enabled: quizMode === 'list',
  });

  const { data: quizWithQuestions } = useQuery({
    queryKey: ['quiz', activeQuiz],
    queryFn: () => quizzesService.getById(activeQuiz),
    enabled: !!activeQuiz && quizMode === 'taking',
  });

  const { data: attempts } = useQuery({
    queryKey: ['quizAttempts', activeQuiz],
    queryFn: () => quizzesService.getAttempts(activeQuiz),
    enabled: !!activeQuiz && quizMode === 'results',
  });

  const submitMutation = useMutation({
    mutationFn: ({ quizId, data }) => quizzesService.submitAttempt(quizId, data),
    onSuccess: (result) => {
      setQuizResult(result);
      setQuizMode('results');
      queryClient.invalidateQueries(['quizAttempts']);
    },
  });

  const handleStartQuiz = (quizId) => {
    setActiveQuiz(quizId);
    setQuizMode('taking');
    setAnswers({});
    setQuizResult(null);
  };

  const handleAnswerChange = (questionId, answer) => {
    setAnswers({ ...answers, [questionId]: answer });
  };

  const handleSubmitQuiz = () => {
    if (activeQuiz) {
      submitMutation.mutate({
        quizId: activeQuiz,
        data: { answers: JSON.stringify(answers) }
      });
    }
  };

  if (isLoading) return <div>Loading quizzes...</div>;

  if (quizMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Quizzes</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {quizzes?.map((quiz) => (
            <div key={quiz.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center gap-2 mb-2">
                <Award className="text-purple-600 dark:text-purple-400" size={20} />
                <h3 className="font-semibold text-gray-900 dark:text-white">{quiz.title}</h3>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{quiz.description}</p>
              <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-3">
                <span className="flex items-center gap-1">
                  <Clock size={14} />
                  {quiz.time_limit ? `${quiz.time_limit} min` : 'No limit'}
                </span>
                <span className={`px-2 py-1 rounded ${
                  quiz.difficulty === 'easy' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                  quiz.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                  'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {quiz.difficulty}
                </span>
              </div>
              <button
                onClick={() => handleStartQuiz(quiz.id)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center justify-center gap-2"
              >
                <Play size={16} />
                Start Quiz
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (quizMode === 'taking' && quizWithQuestions) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{quizWithQuestions.title}</h2>
          <button
            onClick={() => setQuizMode('list')}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Back to List
          </button>
        </div>

        <div className="space-y-6">
          {quizWithQuestions.questions.map((question, index) => (
            <div key={question.id} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">
                {index + 1}. {question.question_text}
              </h3>
              <div className="space-y-2">
                {question.question_type === 'multiple_choice' && question.options && (
                  JSON.parse(question.options).map((option, optIndex) => (
                    <label key={optIndex} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name={`question-${question.id}`}
                        value={option}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        className="w-4 h-4"
                      />
                      <span className="text-gray-700 dark:text-gray-300">{option}</span>
                    </label>
                  ))
                )}
                {question.question_type === 'text' && (
                  <textarea
                    placeholder="Type your answer..."
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                    rows="3"
                  />
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 flex justify-end">
          <button
            onClick={handleSubmitQuiz}
            disabled={submitMutation.isLoading}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
          >
            {submitMutation.isLoading ? 'Submitting...' : 'Submit Quiz'}
          </button>
        </div>
      </div>
    );
  }

  if (quizMode === 'results' && quizResult) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Quiz Results</h2>
          <button
            onClick={() => setQuizMode('list')}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            Back to List
          </button>
        </div>

        <div className="text-center mb-8">
          <div className="text-6xl font-bold text-gray-900 dark:text-white mb-2">
            {quizResult.score.toFixed(1)}%
          </div>
          <p className="text-gray-600 dark:text-gray-400">
            You scored {quizResult.total_points - (quizResult.score * quizResult.total_points / 100).toFixed(0)} out of {quizResult.total_points} points
          </p>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <List size={20} />
            Previous Attempts
          </h3>
          {attempts && attempts.length > 0 ? (
            <div className="space-y-2">
              {attempts.map((attempt) => (
                <div key={attempt.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <span className="text-gray-900 dark:text-white">
                    {attempt.completed_at ? new Date(attempt.completed_at).toLocaleString() : 'In progress'}
                  </span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {attempt.score?.toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600 dark:text-gray-400">No previous attempts</p>
          )}
        </div>
      </div>
    );
  }

  return null;
}
