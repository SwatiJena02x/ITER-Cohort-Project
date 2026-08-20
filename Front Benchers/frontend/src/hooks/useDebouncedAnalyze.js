import { useRef, useCallback, useEffect } from 'react';

/**
 * Custom hook that debounces the /analyze API call.
 */
export function useDebouncedAnalyze(delay = 2000) {
  const abortRef = useRef(null);
  const timeoutRef = useRef(null);

  const instantAnalyze = useCallback(
    async (problemId, code, persona, previousComments, onResult) => {
      // Abort any in-flight request
      if (abortRef.current) {
        abortRef.current.abort();
      }

      // Don't analyze if code is too short
      if (!code || code.trim().length < 20) return;

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        const response = await fetch('http://localhost:8000/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            problem_id: problemId,
            code: code,
            persona: persona,
            previous_comments: previousComments || [],
          }),
          signal: controller.signal,
        });

        if (!response.ok) throw new Error('Analyze request failed');

        const data = await response.json();
        onResult(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Analyze error:', err);
        }
      }
    },
    []
  );

  const debouncedAnalyze = useCallback(
    (...args) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      timeoutRef.current = setTimeout(() => {
        instantAnalyze(...args);
      }, delay);
    },
    [instantAnalyze, delay]
  );

  const cancel = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return cancel;
  }, [cancel]);

  return { debouncedAnalyze, cancel };
}
