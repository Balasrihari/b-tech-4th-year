import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Zap, Clock, TrendingUp, AlertTriangle, Activity, BarChart3 } from 'lucide-react';
import api from '../services/api';

const AIUsageStatistics = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-ai-stats'],
    queryFn: () => api.get('/admin/statistics/ai-usage').then(res => res.data),
  });

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading AI usage statistics...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">AI Usage Statistics</h2>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <Zap size={24} className="text-blue-600 dark:text-blue-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Requests</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.total_ai_requests || 0)}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <Activity size={24} className="text-green-600 dark:text-green-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Tokens Used</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.total_tokens_used || 0)}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 size={24} className="text-purple-600 dark:text-purple-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Tokens/Request</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.average_tokens_per_request || 0)}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <Clock size={24} className="text-orange-600 dark:text-orange-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Response Time</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{(stats?.average_response_time_ms || 0).toFixed(0)}ms</p>
        </div>
      </div>

      {/* Time Period Stats */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Requests Over Time</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Last 24 Hours</p>
            <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{formatNumber(stats?.requests_last_24h || 0)}</p>
          </div>

          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Last 7 Days</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{formatNumber(stats?.requests_last_7d || 0)}</p>
          </div>

          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Last 30 Days</p>
            <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{formatNumber(stats?.requests_last_30d || 0)}</p>
          </div>
        </div>
      </div>

      {/* Requests by Type */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Requests by Type</h3>
        <div className="space-y-3">
          {Object.entries(stats?.requests_by_type || {}).map(([type, count]) => {
            const percentage = stats?.total_ai_requests > 0 ? (count / stats.total_ai_requests * 100).toFixed(1) : 0;
            const labels = {
              chat: 'AI Chat',
              document_qa: 'Document Q&A',
              quiz_generation: 'Quiz Generation',
              roadmap_generation: 'Roadmap Generation',
              recommendations: 'Recommendations',
            };
            const colors = {
              chat: 'bg-blue-500',
              document_qa: 'bg-green-500',
              quiz_generation: 'bg-purple-500',
              roadmap_generation: 'bg-orange-500',
              recommendations: 'bg-pink-500',
            };
            return (
              <div key={type}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {labels[type] || type}
                  </span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {formatNumber(count)} ({percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${colors[type] || 'bg-gray-500'}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Error Rate */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertTriangle size={24} className="text-red-600 dark:text-red-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Error Rate</h3>
          </div>
          <div className="text-right">
            <p className={`text-3xl font-bold ${stats?.error_rate > 5 ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400'}`}>
              {stats?.error_rate.toFixed(2)}%
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {stats?.error_rate > 5 ? 'High error rate' : 'Healthy'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIUsageStatistics;
