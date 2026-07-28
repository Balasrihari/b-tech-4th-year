import api from './api';

export const studyPlansService = {
  getAll: (includeCompleted) => api.get('/study-plans/', { params: { include_completed: includeCompleted } }),
  create: (data) => api.post('/study-plans/', data),
  update: (id, data) => api.put(`/study-plans/${id}`, data),
  delete: (id) => api.delete(`/study-plans/${id}`),
  getRecommendations: () => api.get('/study-plans/recommendations'),
  getRoadmap: () => api.get('/study-plans/roadmap'),
};
