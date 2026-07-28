import { useQuery } from '@tanstack/react-query';
import { learningService } from '../services/learning';
import { studyPlansService } from '../services/studyPlans';
import { TrendingUp, Clock, AlertTriangle, BookOpen, Target, Calendar } from 'lucide-react';

export default function LearningAnalytics() {
  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['learningAnalytics'],
    queryFn: learningService.getAnalytics,
  });

  const { data: roadmap } = useQuery({
    queryKey: ['studyRoadmap'],
    queryFn: studyPlansService.getRoadmap,
  });

  const { data: recommendations } = useQuery({
    queryKey: ['studyRecommendations'],
    queryFn: studyPlansService.getRecommendations,
  });

  if (analyticsLoading) return <div>Loading analytics...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <BookOpen className="text-blue-600 dark:text-blue-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Topics Studied</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{analytics?.total_topics || 0}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className="text-green-600 dark:text-green-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Avg Mastery</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{analytics?.average_mastery || 0}%</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <Clock className="text-purple-600 dark:text-purple-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Study Time</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{analytics?.total_time_spent_hours || 0}h</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="text-orange-600 dark:text-orange-400" size={24} />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Weak Topics</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{analytics?.weak_topic_count || 0}</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Mastery Distribution</h3>
        <div className="flex gap-4">
          <div className="flex-1">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Mastered (80%+)</div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
              <div
                className="bg-green-600 h-4 rounded-full"
                style={{ width: `${(analytics?.mastery_distribution?.mastered / (analytics?.total_topics || 1)) * 100}%` }}
              />
            </div>
            <div className="text-sm text-gray-900 dark:text-white mt-1">{analytics?.mastery_distribution?.mastered || 0} topics</div>
          </div>
          <div className="flex-1">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Learning (50-79%)</div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
              <div
                className="bg-yellow-600 h-4 rounded-full"
                style={{ width: `${(analytics?.mastery_distribution?.learning / (analytics?.total_topics || 1)) * 100}%` }}
              />
            </div>
            <div className="text-sm text-gray-900 dark:text-white mt-1">{analytics?.mastery_distribution?.learning || 0} topics</div>
          </div>
          <div className="flex-1">
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-1">Struggling (&lt;50%)</div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
              <div
                className="bg-red-600 h-4 rounded-full"
                style={{ width: `${(analytics?.mastery_distribution?.struggling / (analytics?.total_topics || 1)) * 100}%` }}
              />
            </div>
            <div className="text-sm text-gray-900 dark:text-white mt-1">{analytics?.mastery_distribution?.struggling || 0} topics</div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Target size={20} />
            Study Recommendations
          </h3>
          {recommendations && recommendations.length > 0 ? (
            <div className="space-y-3">
              {recommendations.map((rec, index) => (
                <div key={index} className="p-3 border border-gray-200 dark:border-gray-700 rounded-lg">
                  <div className="flex justify-between items-start mb-1">
                    <h4 className="font-semibold text-gray-900 dark:text-white">{rec.topic}</h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      rec.priority === 'high' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                      'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    }`}>
                      {rec.priority}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">{rec.reason}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Suggested: {rec.suggested_hours} hours</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600 dark:text-gray-400">No recommendations at this time</p>
          )}
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <Calendar size={20} />
            Study Roadmap
          </h3>
          {roadmap && (
            <div className="space-y-4">
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Not Started</h4>
                {roadmap.not_started?.length > 0 ? (
                  <ul className="space-y-1">
                    {roadmap.not_started.map((item, index) => (
                      <li key={index} className="text-sm text-gray-600 dark:text-gray-400">
                        • {item.topic}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-500">None</p>
                )}
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">In Progress</h4>
                {roadmap.in_progress?.length > 0 ? (
                  <ul className="space-y-1">
                    {roadmap.in_progress.map((item, index) => (
                      <li key={index} className="text-sm text-gray-600 dark:text-gray-400">
                        • {item.topic} ({item.mastery_level}% mastery)
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-500">None</p>
                )}
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Mastered</h4>
                {roadmap.mastered?.length > 0 ? (
                  <ul className="space-y-1">
                    {roadmap.mastered.map((item, index) => (
                      <li key={index} className="text-sm text-gray-600 dark:text-gray-400">
                        • {item.topic} ({item.mastery_level}% mastery)
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 dark:text-gray-500">None</p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
