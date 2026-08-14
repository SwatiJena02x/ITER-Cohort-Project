import { useRef, useCallback } from 'react';

/**
 * Custom hook that immediately fires the /analyze API call.
 */
export function useDebouncedAnalyze() {
  const abortRef = useRef(null);

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

  const cancel = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
    }
  }, []);

  return { debouncedAnalyze: instantAnalyze, cancel };
}
