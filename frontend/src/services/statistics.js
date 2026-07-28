import api from './api';

export const statisticsService = {
  getSystem: () => api.get('/statistics/system'),
  getUser: () => api.get('/statistics/user'),
};
