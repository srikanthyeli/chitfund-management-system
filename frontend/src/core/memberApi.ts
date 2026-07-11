import axios from 'axios';
import { useMemberAuthStore } from '../store/memberAuthStore';

const API_URL = import.meta.env.VITE_API_URL || '';

const memberApi = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to attach member token
memberApi.interceptors.request.use(
  (config) => {
    const state = useMemberAuthStore.getState();
    const token = state.token;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh and unauthorized access
memberApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    // If 401 Unauthorized, we can either attempt refresh or just log them out.
    // For now, if unauthorized and not a login request, log them out.
    const originalRequest = error.config;
    if (error.response?.status === 401 && originalRequest.url !== '/member/auth/login') {
        const state = useMemberAuthStore.getState();
        state.logout();
        window.location.href = '/member/login';
    }
    return Promise.reject(error);
  }
);

export default memberApi;
