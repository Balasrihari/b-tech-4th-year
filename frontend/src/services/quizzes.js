import api from './api';

export const quizzesService = {
  getAll: (courseId) => api.get('/quizzes/', { params: { course_id: courseId } }),
  getById: (id) => api.get(`/quizzes/${id}`),
  create: (data) => api.post('/quizzes/', data),
  addQuestion: (quizId, data) => api.post(`/quizzes/${quizId}/questions`, data),
  submitAttempt: (quizId, data) => api.post(`/quizzes/${quizId}/attempt`, data),
  getAttempts: (quizId) => api.get(`/quizzes/${quizId}/attempts`),
  update: (id, data) => api.put(`/quizzes/${id}`, data),
  delete: (id) => api.delete(`/quizzes/${id}`),
  
  // Phase 11: New endpoints
  generateQuestions: (params) => api.get('/quizzes/generate-questions', { params }),
  createQuestionBank: (data) => api.post('/quizzes/question-bank', data),
  getQuestionBanks: (topic) => api.get('/quizzes/question-bank', { params: { topic } }),
  getQuestionBankQuestions: (bankId) => api.get(`/quizzes/question-bank/${bankId}/questions`),
  generateAdaptiveQuiz: (data) => api.post('/quizzes/adaptive', data),
  getQuizHistory: (params) => api.get('/quizzes/history', { params }),
  getPerformanceAnalytics: (params) => api.get('/quizzes/performance-analytics', { params }),
};
