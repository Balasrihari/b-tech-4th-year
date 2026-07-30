import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { aiFeaturesService } from '../services/aiFeatures';
import { learningService } from '../services/learning';
import { Lightbulb, TrendingUp, Target, Loader2, BookOpen } from 'lucide-react';

const AIRecommendations = () => {
  const [selectedTopic, setSelectedTopic] = useState('');

  const { data: weakTopics = [] } = useQuery({
    queryKey: ['learning', 'weak-topics'],
    queryFn: () => learningService.getWeakTopics(),
  });

  const { data: progress = [] } = useQuery({
    queryKey: ['learning', 'progress'],
    queryFn: () => learningService.getProgress(),
  });

  const recommendationMutation = useMutation({
    mutationFn: (topic) => aiFeaturesService.explainConcept(topic, 'intermediate'),
  });

  const handleGetRecommendation = (topic) => {
    setSelectedTopic(topic);
    recommendationMutation.mutate(topic);
  };

  const getRecommendations = () => {
    const recommendations = [];

    // Based on weak topics
    if (weakTopics.length > 0) {
      weakTopics.slice(0, 3).forEach((topic) => {
        recommendations.push({
          type: 'weak_topic',
          title: `Focus on ${topic.topic_name}`,
          description: `Your performance in ${topic.topic_name} is below target. Spend more time practicing.`,
          priority: 'high',
          action: () => handleGetRecommendation(topic.topic_name),
          actionLabel: 'Get Study Tips',
        });
      });
    }

    // Based on progress
    if (progress.length > 0) {
      const avgProgress = progress.reduce((sum, p) => sum + (p.mastery_level || 0), 0) / progress.length;
      if (avgProgress < 50) {
        recommendations.push({
          type: 'progress',
          title: 'Increase Study Time',
          description: 'Your overall progress is below 50%. Consider increasing your daily study hours.',
          priority: 'medium',
          action: () => handleGetRecommendation('effective study techniques'),
          actionLabel: 'Learn Study Techniques',
        });
      }
    }

    // General recommendations
    recommendations.push(
      {
        type: 'general',
        title: 'Practice Spaced Repetition',
        description: 'Use flashcards with spaced repetition to improve long-term retention.',
        priority: 'medium',
        action: () => handleGetRecommendation('spaced repetition learning'),
        actionLabel: 'Learn More',
      },
      {
        type: 'general',
        title: 'Take Regular Quizzes',
        description: 'Test your knowledge regularly with AI-generated quizzes to identify gaps.',
        priority: 'low',
        action: () => handleGetRecommendation('effective quiz preparation'),
        actionLabel: 'Get Tips',
      },
      {
        type: 'general',
        title: 'Review Past Mistakes',
        description: 'Analyze your quiz mistakes to understand patterns and avoid repeating errors.',
        priority: 'medium',
        action: () => handleGetRecommendation('learning from mistakes'),
        actionLabel: 'Learn Strategies',
      }
    );

    return recommendations;
  };

  const recommendations = getRecommendations();

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high':
        return <Target size={16} className="text-red-600 dark:text-red-400" />;
      case 'medium':
        return <TrendingUp size={16} className="text-yellow-600 dark:text-yellow-400" />;
      case 'low':
        return <BookOpen size={16} className="text-green-600 dark:text-green-400" />;
      default:
        return <Lightbulb size={16} className="text-gray-600 dark:text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-3 bg-purple-100 dark:bg-purple-900 rounded-lg">
          <Lightbulb size={24} className="text-purple-600 dark:text-purple-400" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI Recommendations</h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">Personalized learning recommendations based on your performance</p>
        </div>
      </div>

      {/* Recommendations List */}
      <div className="grid gap-4">
        {recommendations.map((rec, idx) => (
          <div
            key={idx}
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-3">
                {getPriorityIcon(rec.priority)}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{rec.title}</h3>
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs mt-1 ${getPriorityColor(rec.priority)}`}>
                    {rec.priority.toUpperCase()} PRIORITY
                  </span>
                </div>
              </div>
            </div>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{rec.description}</p>
            <button
              onClick={rec.action}
              disabled={recommendationMutation.isLoading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {recommendationMutation.isLoading && selectedTopic === rec.title ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <Lightbulb size={16} />
                  {rec.actionLabel}
                </>
              )}
            </button>
          </div>
        ))}
      </div>

      {/* AI Explanation */}
      {recommendationMutation.data && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 mb-4">
            <Lightbulb size={20} className="text-purple-600 dark:text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI Insights</h3>
          </div>
          <div className="prose dark:prose-invert max-w-none text-gray-700 dark:text-gray-300">
            {recommendationMutation.data.explanation.split('\n').map((paragraph, idx) => (
              <p key={idx} className="mb-3">{paragraph}</p>
            ))}
          </div>
        </div>
      )}

      {recommendations.length === 0 && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <Lightbulb size={48} className="mx-auto mb-4 text-gray-300 dark:text-gray-600" />
          <p className="text-lg">No recommendations yet</p>
          <p className="text-sm">Complete some quizzes and track your progress to get personalized recommendations</p>
        </div>
      )}
    </div>
  );
};

export default AIRecommendations;
