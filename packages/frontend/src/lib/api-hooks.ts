import { useQuery, useMutation, UseQueryOptions, UseMutationOptions, QueryClient } from '@tanstack/react-query'
import { apiClient } from './backend-api'
import { ApiError } from './api-error'

// Create a client
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 30 * 60 * 1000, // 30 minutes (formerly cacheTime)
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

// Types
export type PortfolioAnalysisResponse = any

// Hooks

export function useProcessarOperacoes(options?: UseMutationOptions<any, ApiError, any>) {
  return useMutation<any, ApiError, any>({
    mutationFn: async (data) => {
      const response = await apiClient.axios.post("/api/v1/processar_operacoes", data);
      return response.data;
    },
    ...options,
  });
}

export function useFrontierData(assets: string[], options?: UseQueryOptions<any, ApiError>) {
  return useQuery<any, ApiError>({
    queryKey: ['frontier', assets.sort().join(',')],
    queryFn: async () => {
      if (assets.length === 0) return null;
      // Using the Next.js API route that proxies to backend or direct backend call?
      // Since apiClient is configured with base URL, we can likely call backend directly if endpoints match.
      // But typically frontier data might be a separate endpoint or part of portfolio analysis.
      // Assuming a dedicated endpoint or parameter.
      // For now, let's assume there's a POST endpoint for this or we reuse processar_operacoes with specific flags
      // detailed in the optimization plan.
      
      // If we don't have a specific endpoint defined in 'endpoints' (Zodios), we might need to use raw axios or add it.
      // Let's use raw axios from apiClient for flexibility if needed.
      const response = await apiClient.axios.post("/api/v1/processar_operacoes", {
        operacoes: [], // We need context here, usually passed via args.
        // If this is just for frontier of specific assets:
        assets: assets,
        analyses: ['efficient_frontier'] 
      });
      return response.data;
    },
    enabled: assets.length > 0,
    staleTime: 10 * 60 * 1000, // 10 minutes
    ...options,
  });
}
