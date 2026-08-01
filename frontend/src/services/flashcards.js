import api from './api';

export const flashcardsService = {
  getAll: (deckName) => api.get('/flashcards/', { params: { deck_name: deckName } }),
  getById: (id) => api.get(`/flashcards/${id}`),
  create: (data) => api.post('/flashcards/', data),
  update: (id, data) => api.put(`/flashcards/${id}`, data),
  delete: (id) => api.delete(`/flashcards/${id}`),
  getDecks: () => api.get('/flashcards/decks'),
  getForReview: () => api.get('/flashcards/review'),
  submitReview: (data) => api.post('/flashcards/review', data),
  
  // Phase 12: New endpoints
  getDeckStatistics: () => api.get('/flashcards/decks/statistics'),
  getProgress: (params) => api.get('/flashcards/progress', { params }),
  getStudySchedule: (params) => api.get('/flashcards/schedule', { params }),
  createBatch: (data) => api.post('/flashcards/batch', data),
  updateDeckName: (deckName, newDeckName) => api.put(`/flashcards/decks/${deckName}`, null, { params: { new_deck_name: newDeckName } }),
};
