import { useState, useEffect, useCallback } from 'react';
import { ApiError } from '../lib/api-error';

interface UseApiOptions<T> {
  initialData?: T;
  skip?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: ApiError) => void;
}

export function useApi<T, P extends any[]>(
  asyncFunction: (...args: P) => Promise<T>,
  options?: UseApiOptions<T>
) {
  const { initialData = null, skip = false, onSuccess, onError } = options || {};

  const [data, setData] = useState<T | null>(initialData);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | null>(null);

  const execute = useCallback(async (...args: P) => {
    setLoading(true);
    setError(null);
    try {
      const result = await asyncFunction(...args);
      setData(result);
      if (onSuccess) {
        onSuccess(result);
      }
      return result;
    } catch (err: any) {
      // If err is already an ApiError (from backend-api interceptor), use it directly
      let apiError: ApiError;
      
      if (err.status_code && err.error) {
         apiError = err as ApiError;
      } else {
        apiError = {
          error: err.response?.data?.error || 'unknown_error',
          message: err.response?.data?.message || err.message,
          status_code: err.response?.status || 500,
          details: err.response?.data?.details,
          request_id: err.response?.data?.request_id,
        };
      }
      
      setError(apiError);
      if (onError) {
        onError(apiError);
      }
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, [asyncFunction, onSuccess, onError]);

  useEffect(() => {
    if (!skip) {
      (execute as () => void)();
    }
  }, [execute, skip]);

  return { data, loading, error, execute };
}