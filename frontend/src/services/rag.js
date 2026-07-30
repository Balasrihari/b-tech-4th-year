import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const ragService = {
  async retrieve(query, topK = 3, useHybrid = true, rerank = true, compress = true) {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/rag/retrieve`,
      { query, top_k: topK, use_hybrid: useHybrid, rerank, compress },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async checkHealth() {
    const response = await axios.get(`${API_URL}/rag/health`);
    return response.data;
  },
};
