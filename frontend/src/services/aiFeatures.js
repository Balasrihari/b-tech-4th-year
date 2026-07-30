import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const aiFeaturesService = {
  async generateQuiz(topic, numQuestions = 5, difficulty = 'medium') {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/quiz/generate`,
      { topic, num_questions: numQuestions, difficulty },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async generateFlashcards(topic, numCards = 10) {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/flashcards/generate`,
      { topic, num_cards: numCards },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async summarizeText(text, maxLength = 200) {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/text/summarize`,
      { text, max_length: maxLength },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async answerQuestion(question, useRag = true) {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/qa/answer`,
      { question, use_rag: useRag },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async generateStudyPlan(subject, durationWeeks = 4, hoursPerWeek = 10) {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/study-plan/generate`,
      { subject, duration_weeks: durationWeeks, hours_per_week: hoursPerWeek },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async explainConcept(concept, level = 'intermediate') {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/concept/explain`,
      { concept, level },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async explainCode(code, language = 'python') {
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${API_URL}/ai/code/explain`,
      { code, language },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  },

  async checkHealth() {
    const response = await axios.get(`${API_URL}/ai/health`);
    return response.data;
  },
};
