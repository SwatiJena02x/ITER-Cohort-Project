import './ResultsPanel.css';

const ResultsPanel = ({ results, isExecuting }) => {
  if (isExecuting) {
    return (
      <div className="results-panel" id="results-panel">
        <div className="results-loading">
          <div className="loading-spinner"></div>
          <p>Executing your code against test cases...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="results-panel" id="results-panel">
        <div className="results-empty">
          <span className="empty-icon">▶</span>
          <p>Click "Run Code" to test your solution against the test cases</p>
        </div>
      </div>
    );
  }

  if (results.error) {
    return (
      <div className="results-panel" id="results-panel">
        <div className="results-error">
          <span className="error-icon">⚠️</span>
          <p>{results.error}</p>
        </div>
      </div>
    );
  }

  const passedCount = results.results.filter((r) => r.passed).length;
  const totalCount = results.results.length;

  return (
    <div className="results-panel" id="results-panel">
      {/* Summary */}
      <div className={`results-summary ${results.passed ? 'all-passed' : 'some-failed'}`}>
        <span className="summary-icon">{results.passed ? '✅' : '❌'}</span>
        <span className="summary-text">
          {results.passed
            ? 'All test cases passed!'
            : `${passedCount}/${totalCount} test cases passed`}
        </span>
      </div>

      {/* Individual results */}
      <div className="results-list">
        {results.results.map((r, i) => (
          <div key={i} className={`result-item ${r.passed ? 'passed' : 'failed'}`}>
            <div className="result-header">
              <span className="result-status">{r.passed ? '✓' : '✗'}</span>
              <span className="result-label">Test Case {i + 1}</span>
            </div>
            <div className="result-detail">
              <div className="result-row">
                <span className="result-key">Input:</span>
                <code className="result-value">{JSON.stringify(r.input)}</code>
              </div>
              <div className="result-row">
                <span className="result-key">Expected:</span>
                <code className="result-value result-expected">{JSON.stringify(r.expected)}</code>
              </div>
              <div className="result-row">
                <span className="result-key">Actual:</span>
                <code className={`result-value ${r.passed ? 'result-correct' : 'result-wrong'}`}>
                  {JSON.stringify(r.actual)}
                </code>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ResultsPanel;
