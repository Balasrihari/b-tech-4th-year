import api from './api';

export const learningService = {
  getProgress: () => api.get('/learning/progress'),
  createProgress: (data) => api.post('/learning/progress', data),
  updateProgress: (id, data) => api.put(`/learning/progress/${id}`, data),
  deleteProgress: (id) => api.delete(`/learning/progress/${id}`),
  getWeakTopics: () => api.get('/learning/weak-topics'),
  createWeakTopic: (data) => api.post('/learning/weak-topics', data),
  updateWeakTopic: (id, data) => api.put(`/learning/weak-topics/${id}`, data),
  deleteWeakTopic: (id) => api.delete(`/learning/weak-topics/${id}`),
  getAnalytics: () => api.get('/learning/analytics'),
  
  // Phase 13: New endpoints
  getDashboardOverview: () => api.get('/learning/dashboard'),
  getComprehensiveAnalytics: (params) => api.get('/learning/comprehensive', { params }),
  getLearningTrends: (params) => api.get('/learning/trends', { params }),
  getStudyStatistics: () => api.get('/learning/statistics'),
  getTopicPerformance: () => api.get('/learning/topic-performance'),
  getTimeAnalytics: (params) => api.get('/learning/time-analytics', { params }),
};
