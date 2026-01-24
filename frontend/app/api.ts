import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost/api",
});

// Request interceptor - adds auth token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;

      if (status === 401) {
        // Unauthorized - token invalid or expired
        localStorage.removeItem("token");
        // Redirect to login (if in browser context)
        if (typeof window !== "undefined") {
          window.location.href = "/login";
        }
      }

      if (status === 403) {
        console.error("Access denied: You don't have permission for this action");
      }
    }
    return Promise.reject(error);
  }
);

export default api;
