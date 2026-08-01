import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, HardDrive, CheckCircle, Clock, AlertCircle, Database, FileText as FileIcon } from 'lucide-react';
import api from '../services/api';

const DocumentStatistics = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['admin-document-stats'],
    queryFn: () => api.get('/admin/statistics/documents').then(res => res.data),
  });

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat().format(num);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading document statistics...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Document Statistics</h2>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <FileText size={24} className="text-blue-600 dark:text-blue-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Documents</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.total_documents || 0)}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <HardDrive size={24} className="text-green-600 dark:text-green-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Storage Used</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatBytes(stats?.total_storage_used_bytes || 0)}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <Database size={24} className="text-purple-600 dark:text-purple-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Unique Users</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.documents_by_user || 0)}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-2">
            <FileIcon size={24} className="text-orange-600 dark:text-orange-400" />
            <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg File Size</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatBytes(stats?.average_file_size || 0)}</p>
        </div>
      </div>

      {/* Processing Status */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Processing Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <CheckCircle size={32} className="text-green-600 dark:text-green-400" />
            <div>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{formatNumber(stats?.documents_processed || 0)}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
            <Clock size={32} className="text-yellow-600 dark:text-yellow-400" />
            <div>
              <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{formatNumber(stats?.documents_processing || 0)}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Processing</p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <AlertCircle size={32} className="text-red-600 dark:text-red-400" />
            <div>
              <p className="text-2xl font-bold text-red-600 dark:text-red-400">{formatNumber(stats?.documents_failed || 0)}</p>
              <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Documents by Type */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Documents by Type</h3>
        <div className="space-y-3">
          {Object.entries(stats?.documents_by_type || {}).map(([type, count]) => {
            const percentage = stats?.total_documents > 0 ? (count / stats.total_documents * 100).toFixed(1) : 0;
            const colors = {
              study_material: 'bg-blue-500',
              assignment: 'bg-green-500',
              reference: 'bg-purple-500',
              notes: 'bg-orange-500',
            };
            return (
              <div key={type}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300 capitalize">
                    {type.replace('_', ' ')}
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

      {/* Content Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <FileText size={24} className="text-blue-600 dark:text-blue-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Word Count</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.total_word_count || 0)}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Total words across all documents</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3 mb-4">
            <FileIcon size={24} className="text-purple-600 dark:text-purple-400" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Page Count</h3>
          </div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{formatNumber(stats?.total_page_count || 0)}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Total pages across all documents</p>
        </div>
      </div>
    </div>
  );
};

export default DocumentStatistics;
