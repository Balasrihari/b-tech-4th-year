import api from './api';

export const flashcardsService = {
  getAll: (deckName) => api.get('/flashcards/', { params: { deck_name: deckName } }),
  getDecks: () => api.get('/flashcards/decks'),
  getForReview: (deckName) => api.get('/flashcards/review', { params: { deck_name: deckName } }),
  getById: (id) => api.get(`/flashcards/${id}`),
  create: (data) => api.post('/flashcards/', data),
  update: (id, data) => api.put(`/flashcards/${id}`, data),
  delete: (id) => api.delete(`/flashcards/${id}`),
  submitReview: (data) => api.post('/flashcards/review', data),
};
