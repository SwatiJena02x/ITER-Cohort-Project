import { useState, useCallback, useEffect, useRef } from 'react';
import ProblemSelector from './components/ProblemSelector';
import PersonaSelector from './components/PersonaSelector';
import CodeEditor from './components/CodeEditor';
import AvatarPanel from './components/AvatarPanel';
import CommentFeed from './components/CommentFeed';
import HintPanel from './components/HintPanel';
import ChatPanel from './components/ChatPanel';
import ResultsPanel from './components/ResultsPanel';
import { useDebouncedAnalyze } from './hooks/useDebouncedAnalyze';
import './styles/tokens.css';
import './App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  // ─── State ─────────────────────────────────────────────────────────
  const [problems, setProblems] = useState([]);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [problemDetail, setProblemDetail] = useState(null);
  const [persona, setPersona] = useState('walter_white');
  const [code, setCode] = useState('');
  const [tone, setTone] = useState('neutral_thinking');
  const [comments, setComments] = useState([]);
  const [hintTier, setHintTier] = useState(0);
  const [chatHistory, setChatHistory] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [activePanel, setActivePanel] = useState('chat'); // 'chat' | 'hint' | 'results'
  const [showMobilePanel, setShowMobilePanel] = useState(false);
  const lineCountRef = useRef(0);
  const [personaQuotes, setPersonaQuotes] = useState({ pass_quotes: [], fail_quotes: [] });

  const { debouncedAnalyze, cancel: cancelAnalyze } = useDebouncedAnalyze(2500);

  // ─── Load problems list ─────────────────────────────────────────────
  useEffect(() => {
    let isMounted = true;
    const loadProblems = () => {
      fetch(`${API_BASE}/problems`)
        .then((r) => {
          if (!r.ok) throw new Error('Network response was not ok');
          return r.json();
        })
        .then((data) => {
          if (!isMounted) return;
          setProblems(data);
          if (data.length > 0) {
            setSelectedProblem(data[0].id);
          }
        })
        .catch((err) => {
          if (!isMounted) return;
          console.error('Failed to load problems, retrying in 2s...', err);
          setTimeout(loadProblems, 2000);
        });
    };
    loadProblems();
    return () => { isMounted = false; };
  }, []);

  // ─── Load problem detail when selection changes ─────────────────────
  useEffect(() => {
    if (!selectedProblem) return;
    fetch(`${API_BASE}/problems/${selectedProblem}`)
      .then((r) => r.json())
      .then((data) => {
        setProblemDetail(data);
        setCode(data.starter_code);
        lineCountRef.current = data.starter_code.split('\n').length;
        setComments([]);
        setHintTier(0);
        setChatHistory([]);
        setResults(null);
        setTone('neutral_thinking');
      })
      .catch((err) => console.error('Failed to load problem detail:', err));
  }, [selectedProblem]);

  // ─── Handle code changes with instant analysis on Enter ───────────────
  const handleCodeChange = useCallback(
    (newCode) => {
      setCode(newCode);
      const currentLines = newCode.split('\n').length;
      
      // Only trigger analysis if line count increased (user pressed Enter)
      if (currentLines > lineCountRef.current) {
        setIsAnalyzing(true);

        debouncedAnalyze(
          selectedProblem,
          newCode,
          persona,
          comments.slice(-5).map((c) => c.text),
          (result) => {
            setIsAnalyzing(false);
            if (result.triggered) {
              setTone(result.tone || 'playful_warning');
              setComments((prev) => {
                // Deduplicate: skip if same comment as last one
                if (prev.length > 0 && prev[prev.length - 1].text === result.comment) {
                  return prev;
                }
                return [
                  ...prev,
                  {
                    text: result.comment,
                    tone: result.tone,
                    timestamp: Date.now(),
                  },
                ];
              });
            }
          }
        );
      }
      lineCountRef.current = currentLines;
    },
    [selectedProblem, persona, comments, debouncedAnalyze]
  );

  // ─── Handle persona switch ──────────────────────────────────────────
  const handlePersonaChange = useCallback(
    (newPersona) => {
      setPersona(newPersona);
      cancelAnalyze();
      setComments([]);
      setChatHistory([]);
      setTone('neutral_thinking');
    },
    [cancelAnalyze]
  );

  // ─── Load persona quotes ──────────────────────────────────────────
  useEffect(() => {
    fetch(`${API_BASE}/personas/${persona}`)
      .then((r) => r.json())
      .then((data) => {
        setPersonaQuotes({
          pass_quotes: data.pass_quotes || [],
          fail_quotes: data.fail_quotes || [],
        });
      })
      .catch(() => setPersonaQuotes({ pass_quotes: [], fail_quotes: [] }));
  }, [persona]);

  // ─── Execute code ───────────────────────────────────────────────────
  const handleExecute = useCallback(async () => {
    if (!selectedProblem || !code) return;
    setIsExecuting(true);
    setActivePanel('results');

    try {
      const response = await fetch(`${API_BASE}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: selectedProblem,
          code: code,
        }),
      });
      const data = await response.json();
      setResults(data);

      // Update tone based on results
      if (data.passed) {
        setTone('celebrating');
        const passQuotes = personaQuotes.pass_quotes;
        const quote = passQuotes.length > 0
          ? passQuotes[Math.floor(Math.random() * passQuotes.length)]
          : '✅ All test cases passed!';
        setComments((prev) => [
          ...prev,
          {
            text: quote,
            tone: 'celebrating',
            timestamp: Date.now(),
          },
        ]);
      } else {
        const passedCount = data.results.filter((r) => r.passed).length;
        setTone('encouraging');
        const failQuotes = personaQuotes.fail_quotes;
        const quote = failQuotes.length > 0
          ? failQuotes[Math.floor(Math.random() * failQuotes.length)]
          : `${passedCount}/${data.results.length} test cases passed. Keep going!`;
        setComments((prev) => [
          ...prev,
          {
            text: quote,
            tone: 'encouraging',
            timestamp: Date.now(),
          },
        ]);
      }
    } catch (err) {
      console.error('Execute error:', err);
      setResults({
        passed: false,
        results: [],
        error: 'Failed to execute code. Please try again.',
      });
    } finally {
      setIsExecuting(false);
    }
  }, [selectedProblem, code]);

  // ─── Chat ───────────────────────────────────────────────────────────
  const handleChat = useCallback(
    async (message) => {
      if (!selectedProblem || !message.trim()) return;

      const newHistory = [...chatHistory, { role: 'user', content: message }];
      setChatHistory(newHistory);

      try {
        const response = await fetch(`${API_BASE}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            problem_id: selectedProblem,
            message: message,
            history: chatHistory,
            persona: persona,
          }),
        });
        const data = await response.json();
        setChatHistory((prev) => [...prev, { role: 'assistant', content: data.reply }]);
      } catch (err) {
        console.error('Chat error:', err);
        setChatHistory((prev) => [
          ...prev,
          { role: 'assistant', content: 'Connection lost. Try again.' },
        ]);
      }
    },
    [selectedProblem, chatHistory, persona]
  );

  // ─── Hints ──────────────────────────────────────────────────────────
  const handleHint = useCallback(async () => {
    if (!selectedProblem) return;
    setActivePanel('hint');

    try {
      const response = await fetch(`${API_BASE}/hint`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          problem_id: selectedProblem,
          tier: hintTier,
          persona: persona,
        }),
      });
      const data = await response.json();
      setComments((prev) => [
        ...prev,
        {
          text: `💡 Hint: ${data.hint_text}`,
          tone: 'encouraging',
          timestamp: Date.now(),
        },
      ]);
      if (hintTier < 2) setHintTier((prev) => prev + 1);
    } catch (err) {
      console.error('Hint error:', err);
    }
  }, [selectedProblem, hintTier, persona]);

  // ─── Render ─────────────────────────────────────────────────────────
  return (
    <div className="app">
      {/* ─── Header bar ─── */}
      <header className="app-header">
        <div className="header-left">
          <div className="app-logo">
            <span className="logo-icon">⚡</span>
            <h1 className="logo-text">DSA Coach</h1>
          </div>
          <ProblemSelector
            problems={problems}
            selected={selectedProblem}
            onSelect={setSelectedProblem}
          />
        </div>
        <div className="header-right">
          <PersonaSelector
            selected={persona}
            onSelect={handlePersonaChange}
          />
          <button
            className="mobile-toggle"
            onClick={() => setShowMobilePanel(!showMobilePanel)}
            aria-label="Toggle coach panel"
          >
            🎭
          </button>
        </div>
      </header>

      {/* ─── Main workspace ─── */}
      <main className="workspace">
        {/* ─── Left: Editor column ─── */}
        <div className="editor-column">
          {/* Problem description */}
          {problemDetail && (
            <div className="problem-description">
              <h2 className="problem-title">{problemDetail.title}</h2>
              <span className={`difficulty-badge difficulty-${problemDetail.difficulty.toLowerCase()}`}>
                {problemDetail.difficulty}
              </span>
              <div className="problem-text" dangerouslySetInnerHTML={{
                __html: problemDetail.description
                  .replace(/\n/g, '<br/>')
                  .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                  .replace(/`([^`]+)`/g, '<code>$1</code>')
                  .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
              }} />
            </div>
          )}

          {/* Code editor */}
          <div className={`editor-container ${isAnalyzing ? 'analyzing' : ''}`}>
            <CodeEditor
              code={code}
              onChange={handleCodeChange}
            />
          </div>

          {/* Action bar */}
          <div className="action-bar">
            <button
              className="btn btn-hint"
              onClick={handleHint}
              disabled={hintTier > 2}
              id="hint-button"
            >
              <span className="btn-icon">💡</span>
              Hint {hintTier > 0 ? `(${hintTier}/3)` : ''}
            </button>
            <button
              className="btn btn-run"
              onClick={handleExecute}
              disabled={isExecuting}
              id="run-button"
            >
              <span className="btn-icon">{isExecuting ? '⏳' : '▶'}</span>
              {isExecuting ? 'Running...' : 'Run Code'}
            </button>
          </div>
        </div>

        {/* ─── Right: Coach sidebar ─── */}
        <aside className={`coach-sidebar ${showMobilePanel ? 'mobile-open' : ''}`}>
          {/* Avatar */}
          <AvatarPanel persona={persona} tone={tone} isAnalyzing={isAnalyzing} />

          {/* Comment feed */}
          <CommentFeed comments={comments} />

          {/* Tab bar */}
          <div className="sidebar-tabs">
            <button
              className={`tab-btn ${activePanel === 'chat' ? 'active' : ''}`}
              onClick={() => setActivePanel('chat')}
              id="tab-chat"
            >
              Chat
            </button>
            <button
              className={`tab-btn ${activePanel === 'hint' ? 'active' : ''}`}
              onClick={() => setActivePanel('hint')}
              id="tab-hint"
            >
              Hints
            </button>
            <button
              className={`tab-btn ${activePanel === 'results' ? 'active' : ''}`}
              onClick={() => setActivePanel('results')}
              id="tab-results"
            >
              Results
            </button>
          </div>

          {/* Panel content */}
          <div className="sidebar-panel-content">
            {activePanel === 'chat' && (
              <ChatPanel
                history={chatHistory}
                onSend={handleChat}
                persona={persona}
              />
            )}
            {activePanel === 'hint' && (
              <HintPanel
                hintTier={hintTier}
                onRequestHint={handleHint}
                comments={comments.filter((c) => c.text.startsWith('💡'))}
              />
            )}
            {activePanel === 'results' && (
              <ResultsPanel results={results} isExecuting={isExecuting} />
            )}
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;
