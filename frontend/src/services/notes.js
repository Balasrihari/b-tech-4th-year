import api from './api';

export const notesService = {
  // Get all notes for current user
  getAll: async (params = {}) => {
    const response = await api.get('/notes', { params });
    return response.data;
  },

  // Get a single note by ID
  getById: async (id) => {
    const response = await api.get(`/notes/${id}`);
    return response.data;
  },

  // Create a new note
  create: async (data) => {
    const response = await api.post('/notes', data);
    return response.data;
  },

  // Update a note
  update: async (id, data) => {
    const response = await api.put(`/notes/${id}`, data);
    return response.data;
  },

  // Delete a note
  delete: async (id) => {
    const response = await api.delete(`/notes/${id}`);
    return response.data;
  },

  // Get all unique topics
  getTopics: async () => {
    const response = await api.get('/notes/topics/list');
    return response.data;
  },
};
