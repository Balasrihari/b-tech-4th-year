import api from './api';

export const assignmentsService = {
  // Get all assignments
  getAll: async (params = {}) => {
    const response = await api.get('/assignments', { params });
    return response.data;
  },

  // Get a single assignment by ID
  getById: async (id) => {
    const response = await api.get(`/assignments/${id}`);
    return response.data;
  },

  // Create a new assignment (Faculty only)
  create: async (data) => {
    const response = await api.post('/assignments', data);
    return response.data;
  },

  // Update an assignment (Faculty only)
  update: async (id, data) => {
    const response = await api.put(`/assignments/${id}`, data);
    return response.data;
  },

  // Delete an assignment (Faculty only)
  delete: async (id) => {
    const response = await api.delete(`/assignments/${id}`);
    return response.data;
  },

  // Submit an assignment (Student only)
  submit: async (assignmentId, data) => {
    const response = await api.post(`/assignments/${assignmentId}/submissions`, data);
    return response.data;
  },

  // Get submissions for an assignment
  getSubmissions: async (assignmentId) => {
    const response = await api.get(`/assignments/${assignmentId}/submissions`);
    return response.data;
  },

  // Grade a submission (Faculty only)
  gradeSubmission: async (submissionId, data) => {
    const response = await api.put(`/assignments/submissions/${submissionId}`, data);
    return response.data;
  },

  // Get current user's submissions (Student only)
  getMySubmissions: async () => {
    const response = await api.get('/assignments/my/submissions');
    return response.data;
  },
};
