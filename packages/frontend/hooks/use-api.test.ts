import { renderHook, act } from '@testing-library/react';
import { useApi } from './use-api';
import { ApiError } from '../lib/api-error';

// Mock async function for testing
const mockAsyncFunction = jest.fn();

describe('useApi', () => {
  beforeEach(() => {
    // Clear mock history before each test
    mockAsyncFunction.mockClear();
  });

  it('should not automatically execute if skip is true', () => {
    renderHook(() => useApi(mockAsyncFunction, { skip: true }));
    expect(mockAsyncFunction).not.toHaveBeenCalled();
  });

  it('should automatically execute if skip is false', () => {
    renderHook(() => useApi(mockAsyncFunction, { skip: false }));
    expect(mockAsyncFunction).toHaveBeenCalledTimes(1);
  });

  it('should execute manually when execute is called, even if skip is true', async () => {
    const { result } = renderHook(() => useApi(mockAsyncFunction, { skip: true }));

    await act(async () => {
      await result.current.execute();
    });

    expect(mockAsyncFunction).toHaveBeenCalledTimes(1);
  });

  it('should return data on successful execution', async () => {
    const responseData = { message: 'Success' };
    mockAsyncFunction.mockResolvedValue(responseData);

    const { result, waitForNextUpdate } = renderHook(() => useApi(mockAsyncFunction));

    await waitForNextUpdate();

    expect(result.current.data).toEqual(responseData);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('should return error on failed execution', async () => {
    const error: ApiError = {
      error: 'test_error',
      message: 'An error occurred',
      status_code: 500,
    };
    mockAsyncFunction.mockRejectedValue({ response: { data: error, status: 500 } });

    const { result } = renderHook(() => useApi(mockAsyncFunction));

    await act(async () => {
      await expect(result.current.execute()).rejects.toEqual(error);
    });

    expect(result.current.error?.error).toEqual(error.error);
    expect(result.current.loading).toBe(false);
    expect(result.current.data).toBe(null);
  });

  it('should set loading state during execution', async () => {
    const { result } = renderHook(() => useApi(mockAsyncFunction, { skip: true }));

    const promise = act(async () => {
      await result.current.execute();
    });

    expect(result.current.loading).toBe(true);
    await promise;
    expect(result.current.loading).toBe(false);
  });
});
