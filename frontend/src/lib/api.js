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

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const setupInterceptors = (instance) => {
  // ── Request Interceptor (Mandatory Identity Header) ──
  instance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  }, (err) => Promise.reject(err));

  // ── Response Interceptor (Atomic Refresh Synchronizer) ──
  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      // 401 Unauthorized: Trigger Atomic Refresh cycle
      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          // Queue this request and wait for current refresh to complete
          return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
          })
            .then((token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              return instance(originalRequest);
            })
            .catch((err) => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        return new Promise(async (resolve, reject) => {
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (!refreshToken) throw new Error("No refresh-credential available");

            const res = await axios.post(ENDPOINTS.REFRESH, {}, {
              headers: { Authorization: `Bearer ${refreshToken}` }
            });

            const { access_token, refresh_token } = res.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);

            // Update original request and retry
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            processQueue(null, access_token);
            resolve(instance(originalRequest));
          } catch (refreshErr) {
            processQueue(refreshErr, null);
            localStorage.clear();
            if (window.location.pathname !== '/login') {
              window.location.href = '/login';
            }
            reject(refreshErr);
          } finally {
            isRefreshing = false;
          }
        });
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
