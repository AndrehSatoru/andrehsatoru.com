import axios, { AxiosInstance, AxiosError } from 'axios';
import { z } from 'zod';
import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { endpoints, schemas } from 'shared-types';
import { useAuthStore } from '../hooks/useAuthStore';

// Define the base URL and timeout from environment variables
// Use INTERNAL_API_URL for server-side calls (API routes), NEXT_PUBLIC_API_URL for client-side
const isServer = typeof window === 'undefined';
const API_BASE_URL = isServer 
  ? (process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000')
  : (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000', 10);

// Create a Zodios instance
export const apiClient = new Zodios(endpoints, {
  axiosInstance: axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
  }),
});

// --- Interceptors ---
// Request interceptor for authentication
apiClient.axios.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken; // Get token from store
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and retries
apiClient.axios.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true; // Mark request as retried
      const refreshToken = useAuthStore.getState().refreshToken;

      if (refreshToken) {
        try {
          // Assuming there's a refresh endpoint
          // const response = await api.auth.refresh({ refresh_token: refreshToken });
          // But since it's not defined, perhaps skip for now
        } catch (refreshError) {
          // Handle refresh error
        }
      }
    }
    return Promise.reject(error);
  }
);

// --- Interceptors ---
// Request interceptor for authentication
apiClient.axios.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken; // Get token from store
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and retries
apiClient.axios.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized errors
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true; // Mark request as retried
      const refreshToken = useAuthStore.getState().refreshToken;

      if (refreshToken) {
        try {
          // Attempt to refresh token
          const refreshResponse = await axios.post<{ access_token: string; refresh_token?: string }>(
            `${API_BASE_URL}/api/v1/auth/refresh`,
            null,
            { params: { refresh_token: refreshToken } }
          );

          const newAccessToken = refreshResponse.data.access_token;
          const newRefreshToken = refreshResponse.data.refresh_token || refreshToken; // Use new refresh token if provided

          useAuthStore.getState().setTokens(newAccessToken, newRefreshToken); // Update tokens in store

          // Retry the original request with the new access token
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient.axios(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout user
          useAuthStore.getState().logout();
          // Redirect to login page or show a message
          console.error('Token refresh failed, logging out:', refreshError);
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available, logout user
        useAuthStore.getState().logout();
        console.error('No refresh token available, logging out.');
        return Promise.reject(error);
      }
    }

    // Implement standardized error handling (Phase 4)
    const apiError: ApiError = {
      error: (error.response?.data as any)?.error || 'unknown_error',
      message: (error.response?.data as any)?.message || error.message,
      status_code: error.response?.status || 500,
      details: (error.response?.data as any)?.details,
      request_id: (error.response?.data as any)?.request_id,
    };

    // Note: Toast notifications should be handled in components, not in interceptors
    // since interceptors run on both server and client side
    
    return Promise.reject(apiError);
  }
);

// Helper type for API errors (to be refined in Phase 4)
export type ApiError = {
  error: string;
  message: string;
  status_code: number;
  details?: Record<string, any>;
  request_id?: string;
};

// Export function to send operations
export async function enviarOperacoes(data: any) {
  return await apiClient.post("/api/v1/processar_operacoes", data);
}