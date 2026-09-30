import { useState, useCallback } from 'react';
import axios, { AxiosError } from 'axios';

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: AxiosError) => void;
}

interface UseApiReturn<T> {
  data: T | null;
  loading: boolean;
  error: AxiosError | null;
  execute: (...args: any[]) => Promise<T>;
  reset: () => void;
}

/**
 * Custom hook for API calls with loading and error states
 */
export function useApi<T>(
  apiCall: (...args: any[]) => Promise<T>,
  options?: UseApiOptions
): UseApiReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<AxiosError | null>(null);

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setLoading(true);
        setError(null);
        const result = await apiCall(...args);
        setData(result);
        options?.onSuccess?.(result);
        return result;
      } catch (err: any) {
        const axiosError = err as AxiosError;
        setError(axiosError);
        options?.onError?.(axiosError);
        throw axiosError;
      } finally {
        setLoading(false);
      }
    },
    [apiCall, options]
  );

  const reset = useCallback(() => {
    setData(null);
    setLoading(false);
    setError(null);
  }, []);

  return { data, loading, error, execute, reset };
}

/**
 * Hook for managing API loading state
 */
export function useApiState() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const startLoading = useCallback(() => {
    setLoading(true);
    setError(null);
  }, []);

  const stopLoading = useCallback(() => {
    setLoading(false);
  }, []);

  const setApiError = useCallback((message: string) => {
    setError(message);
    setLoading(false);
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    startLoading,
    stopLoading,
    setApiError,
    clearError,
  };
}
