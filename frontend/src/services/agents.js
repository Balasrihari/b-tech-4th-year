import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const agentsService = {
  async chat(message) {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/agents/chat`,
      { message },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async checkHealth() {
    const response = await axios.get(`${API_URL}/agents/health`);
    return response.data;
  },
};
