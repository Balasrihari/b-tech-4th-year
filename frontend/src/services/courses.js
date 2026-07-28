import api from './api';

export const coursesService = {
  getAll: () => api.get('/courses/'),
  getById: (id) => api.get(`/courses/${id}`),
  create: (data) => api.post('/courses/', data),
  update: (id, data) => api.put(`/courses/${id}`, data),
  delete: (id) => api.delete(`/courses/${id}`),
};
