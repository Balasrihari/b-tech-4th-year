import api from './api';

export const learningService = {
  getProgress: (courseId) => api.get('/learning/progress', { params: { course_id: courseId } }),
  createProgress: (data) => api.post('/learning/progress', data),
  updateProgress: (id, data) => api.put(`/learning/progress/${id}`, data),
  deleteProgress: (id) => api.delete(`/learning/progress/${id}`),
  getWeakTopics: () => api.get('/learning/weak-topics'),
  createWeakTopic: (data) => api.post('/learning/weak-topics', data),
  updateWeakTopic: (id, data) => api.put(`/learning/weak-topics/${id}`, data),
  deleteWeakTopic: (id) => api.delete(`/learning/weak-topics/${id}`),
  getAnalytics: () => api.get('/learning/analytics'),
};
