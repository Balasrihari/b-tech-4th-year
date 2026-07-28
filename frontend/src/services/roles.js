import api from './api';

export const rolesService = {
  // Get all roles
  getAll: async (params = {}) => {
    const response = await api.get('/roles', { params });
    return response.data;
  },

  // Get a single role by ID
  getById: async (id) => {
    const response = await api.get(`/roles/${id}`);
    return response.data;
  },

  // Create a new role
  create: async (data) => {
    const response = await api.post('/roles', data);
    return response.data;
  },

  // Update a role
  update: async (id, data) => {
    const response = await api.put(`/roles/${id}`, data);
    return response.data;
  },

  // Delete a role
  delete: async (id) => {
    const response = await api.delete(`/roles/${id}`);
    return response.data;
  },
};
