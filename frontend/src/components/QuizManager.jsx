import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { quizzesService } from '../services/quizzes';
import { Plus, Play, Clock, Award, List, Sparkles, Database, TrendingUp, History, ArrowLeft } from 'lucide-react';

export default function QuizManager() {
  const [activeQuiz, setActiveQuiz] = useState(null);
  const [quizMode, setQuizMode] = useState('list'); // list, taking, results, generate, question-bank, adaptive, history, analytics
  const [answers, setAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [generateParams, setGenerateParams] = useState({ topic: '', difficulty: 'medium', questionCount: 5 });
  const [adaptiveParams, setAdaptiveParams] = useState({ topic: '', questionCount: 10, timeLimit: 30 });
  const queryClient = useQueryClient();

  const { data: quizzes, isLoading, error } = useQuery({
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

  const { data: quizHistory } = useQuery({
    queryKey: ['quizHistory'],
    queryFn: () => quizzesService.getQuizHistory({ limit: 10, offset: 0 }),
    enabled: quizMode === 'history',
  });

  const { data: performanceAnalytics } = useQuery({
    queryKey: ['quizPerformance'],
    queryFn: () => quizzesService.getPerformanceAnalytics({ days: 30 }),
    enabled: quizMode === 'analytics',
  });

  const submitMutation = useMutation({
    mutationFn: ({ quizId, data }) => quizzesService.submitAttempt(quizId, data),
    onSuccess: (result) => {
      setQuizResult(result);
      setQuizMode('results');
      queryClient.invalidateQueries(['quizAttempts']);
    },
  });

  const generateQuestionsMutation = useMutation({
    mutationFn: (params) => quizzesService.generateQuestions(params),
    onSuccess: (data) => {
      alert(`Generated ${data.questions.length} questions for ${data.topic}`);
      setQuizMode('list');
    },
  });

  const adaptiveQuizMutation = useMutation({
    mutationFn: (data) => quizzesService.generateAdaptiveQuiz(data),
    onSuccess: (quiz) => {
      setActiveQuiz(quiz.id);
      setQuizMode('taking');
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

  const handleGenerateQuestions = (e) => {
    e.preventDefault();
    generateQuestionsMutation.mutate(generateParams);
  };

  const handleGenerateAdaptiveQuiz = (e) => {
    e.preventDefault();
    adaptiveQuizMutation.mutate(adaptiveParams);
  };

  if (isLoading && quizMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">Loading quizzes...</span>
        </div>
      </div>
    );
  }

  if (error && quizMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="text-red-600 dark:text-red-400 text-center py-12">
          <p>Error loading quizzes: {error.message}</p>
          <button onClick={() => queryClient.invalidateQueries(['quizzes'])} className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg">
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (quizMode === 'list') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex flex-wrap justify-between items-center mb-6 gap-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Quizzes</h2>
          <div className="flex gap-2">
            <button
              onClick={() => setQuizMode('generate')}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 flex items-center gap-2"
            >
              <Sparkles size={16} />
              Generate Questions
            </button>
            <button
              onClick={() => setQuizMode('adaptive')}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2"
            >
              <TrendingUp size={16} />
              Adaptive Quiz
            </button>
            <button
              onClick={() => setQuizMode('history')}
              className="px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 flex items-center gap-2"
            >
              <History size={16} />
              History
            </button>
            <button
              onClick={() => setQuizMode('analytics')}
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2"
            >
              <Award size={16} />
              Analytics
            </button>
          </div>
        </div>

        {!quizzes || quizzes.length === 0 ? (
          <div className="text-center py-12 text-gray-600 dark:text-gray-400">
            <p>No quizzes available. Generate questions or create a quiz to get started.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quizzes.map((quiz) => (
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
        )}
      </div>
    );
  }

  if (quizMode === 'generate') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setQuizMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Generate AI Questions</h2>
        </div>

        <form onSubmit={handleGenerateQuestions} className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Topic</label>
            <input
              type="text"
              value={generateParams.topic}
              onChange={(e) => setGenerateParams({ ...generateParams, topic: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="e.g., Python Programming"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Difficulty</label>
            <select
              value={generateParams.difficulty}
              onChange={(e) => setGenerateParams({ ...generateParams, difficulty: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Number of Questions</label>
            <input
              type="number"
              min="1"
              max="20"
              value={generateParams.questionCount}
              onChange={(e) => setGenerateParams({ ...generateParams, questionCount: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            type="submit"
            disabled={generateQuestionsMutation.isLoading}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <Sparkles size={16} />
            {generateQuestionsMutation.isLoading ? 'Generating...' : 'Generate Questions'}
          </button>
        </form>
      </div>
    );
  }

  if (quizMode === 'adaptive') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setQuizMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Generate Adaptive Quiz</h2>
        </div>

        <form onSubmit={handleGenerateAdaptiveQuiz} className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Topic</label>
            <input
              type="text"
              value={adaptiveParams.topic}
              onChange={(e) => setAdaptiveParams({ ...adaptiveParams, topic: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="e.g., Python Programming"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Number of Questions</label>
            <input
              type="number"
              min="1"
              max="20"
              value={adaptiveParams.questionCount}
              onChange={(e) => setAdaptiveParams({ ...adaptiveParams, questionCount: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Time Limit (minutes)</label>
            <input
              type="number"
              min="1"
              value={adaptiveParams.timeLimit}
              onChange={(e) => setAdaptiveParams({ ...adaptiveParams, timeLimit: parseInt(e.target.value) })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            type="submit"
            disabled={adaptiveQuizMutation.isLoading}
            className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <TrendingUp size={16} />
            {adaptiveQuizMutation.isLoading ? 'Generating...' : 'Generate Adaptive Quiz'}
          </button>
        </form>
      </div>
    );
  }

  if (quizMode === 'history') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setQuizMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Quiz History</h2>
        </div>

        {quizHistory ? (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Attempts</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{quizHistory.total_attempts}</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Average Score</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{quizHistory.average_score.toFixed(1)}%</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{quizHistory.completed_count}</p>
              </div>
            </div>

            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Recent Attempts</h3>
            {quizHistory.attempts && quizHistory.attempts.length > 0 ? (
              <div className="space-y-2">
                {quizHistory.attempts.map((attempt) => (
                  <div key={attempt.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <span className="text-gray-900 dark:text-white">
                      Quiz #{attempt.quiz_id}
                    </span>
                    <span className="font-semibold text-gray-900 dark:text-white">
                      {attempt.score?.toFixed(1)}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600 dark:text-gray-400">No quiz attempts yet</p>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
      </div>
    );
  }

  if (quizMode === 'analytics') {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div className="flex items-center gap-2 mb-6">
          <button onClick={() => setQuizMode('list')} className="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">
            <ArrowLeft size={20} />
          </button>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Performance Analytics</h2>
        </div>

        {performanceAnalytics ? (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Average Score</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceAnalytics.average_score.toFixed(1)}%</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Highest Score</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceAnalytics.highest_score.toFixed(1)}%</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Improvement Rate</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceAnalytics.improvement_rate.toFixed(1)}%</p>
              </div>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Attempts</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{performanceAnalytics.total_attempts}</p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Difficulty Distribution</h3>
              <div className="flex gap-4">
                <div className="flex-1 bg-green-100 dark:bg-green-900 rounded-lg p-4">
                  <p className="text-sm text-green-800 dark:text-green-200">Easy: {performanceAnalytics.difficulty_distribution.easy}</p>
                </div>
                <div className="flex-1 bg-yellow-100 dark:bg-yellow-900 rounded-lg p-4">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">Medium: {performanceAnalytics.difficulty_distribution.medium}</p>
                </div>
                <div className="flex-1 bg-red-100 dark:bg-red-900 rounded-lg p-4">
                  <p className="text-sm text-red-800 dark:text-red-200">Hard: {performanceAnalytics.difficulty_distribution.hard}</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Topic Performance</h3>
              {performanceAnalytics.topic_performance && performanceAnalytics.topic_performance.length > 0 ? (
                <div className="space-y-2">
                  {performanceAnalytics.topic_performance.map((topic) => (
                    <div key={topic.quiz_id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <span className="text-gray-900 dark:text-white">{topic.topic}</span>
                      <span className="font-semibold text-gray-900 dark:text-white">{topic.average_score.toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-600 dark:text-gray-400">No topic performance data yet</p>
              )}
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        )}
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
