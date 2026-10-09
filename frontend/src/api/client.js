import axios from "axios";

export const API_ROOT = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

const api = axios.create({ baseURL: `${API_ROOT}/api` });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sd_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    const isLogin = err.config?.url?.includes("auth/login");
    if (err.response?.status === 401 && !isLogin) {
      localStorage.removeItem("sd_token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
