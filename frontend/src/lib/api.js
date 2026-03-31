import axios from 'axios';

const GATEWAY = import.meta.env.VITE_API_GATEWAY || 'http://localhost:80';

const API_BASE    = `${GATEWAY}/api/users`;
const APIKEY_BASE = `${GATEWAY}/api/apikeys`;
const CHAT_BASE   = `${GATEWAY}/api/chat`;

export const ENDPOINTS = {
  LOGIN:           `${API_BASE}/login`,
  REFRESH:         `${API_BASE}/refresh`,
  ME:              `${API_BASE}/me`,
  USERS:           `${API_BASE}/`,
  REGISTER:        `${API_BASE}/register`,
  LOGOUT:          `${API_BASE}/logout`,
  LOGOUT_REFRESH:  `${API_BASE}/logout-refresh`,
  FORGOT_PASSWORD: `${API_BASE}/forgot-password`,
  VERIFY_OTP:      `${API_BASE}/verify-otp`,
  CHANGE_PASSWORD: `${API_BASE}/change-password`,
  APIKEYS:         `${APIKEY_BASE}/`,
  APIKEYS_CREATE:  `${APIKEY_BASE}/create`,

  // Chat service
  CHAT_SESSIONS:   `${CHAT_BASE}/sessions`,
  CHAT_MODELS:     `${CHAT_BASE}/models`,
  CHAT_HEALTH:     `${CHAT_BASE}/health`,
};

const setupInterceptors = (instance) => {
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  });

  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          const refreshToken = localStorage.getItem('refresh_token');
          const res = await axios.post(ENDPOINTS.REFRESH, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          localStorage.setItem('access_token', res.data.access_token);
          localStorage.setItem('refresh_token', res.data.refresh_token);
          return instance(originalRequest);
        } catch (err) {
          localStorage.clear();
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
      }
      return Promise.reject(error);
    }
  );
};

export const api       = axios.create({ baseURL: API_BASE });
export const apikeyApi = axios.create({ baseURL: APIKEY_BASE });
export const chatApi   = axios.create({ baseURL: CHAT_BASE });

setupInterceptors(api);
setupInterceptors(apikeyApi);
setupInterceptors(chatApi);

export default api;
