import { useState, useRef, useEffect } from 'react';
import './ChatPanel.css';

const ChatPanel = ({ history, onSend, persona }) => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
    // Detect when assistant replies (loading stops)
    if (history.length > 0 && history[history.length - 1].role === 'assistant') {
      setIsLoading(false);
    }
  }, [history]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;
    setIsLoading(true);
    onSend(message.trim());
    setMessage('');
    inputRef.current?.focus();
  };

  const PERSONA_NAMES = {
    walter_white: 'Walter',
    kratos: 'Kratos',
    thanos: 'Thanos',
  };

  return (
    <div className="chat-panel" id="chat-panel">
      {/* Messages */}
      <div className="chat-messages" ref={messagesRef}>
        {history.length === 0 ? (
          <div className="chat-empty">
            <p>Ask {PERSONA_NAMES[persona] || 'your coach'} anything about the problem...</p>
          </div>
        ) : (
          history.map((msg, i) => (
            <div key={i} className={`chat-msg chat-${msg.role}`}>
              <span className="chat-role">
                {msg.role === 'user' ? 'You' : PERSONA_NAMES[persona]}
              </span>
              <p className="chat-content">{msg.content}</p>
            </div>
          ))
        )}
        {isLoading && (
          <div className="chat-msg chat-assistant">
            <span className="chat-role">{PERSONA_NAMES[persona]}</span>
            <p className="chat-content chat-typing">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </p>
          </div>
        )}
      </div>

      {/* Input */}
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="text"
          className="chat-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={`Ask ${PERSONA_NAMES[persona] || 'coach'}...`}
          disabled={isLoading}
          id="chat-input"
        />
        <button
          type="submit"
          className="chat-send-btn"
          disabled={!message.trim() || isLoading}
          id="chat-send"
        >
          →
        </button>
      </form>
    </div>
  );
};

export default ChatPanel;
