import api from './api';

export const auditLogsService = {
  // Get all audit logs
  getAll: async (params = {}) => {
    const response = await api.get('/audit-logs', { params });
    return response.data;
  },

  // Get all unique actions
  getActions: async () => {
    const response = await api.get('/audit-logs/actions');
    return response.data;
  },

  // Get all unique resource types
  getResourceTypes: async () => {
    const response = await api.get('/audit-logs/resource-types');
    return response.data;
  },
};
