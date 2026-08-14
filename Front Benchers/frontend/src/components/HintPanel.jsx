import './HintPanel.css';

const HintPanel = ({ hintTier, onRequestHint, comments }) => {
  const hintComments = comments || [];
  const maxTier = 3;

  return (
    <div className="hint-panel" id="hint-panel">
      {/* Tier progress */}
      <div className="hint-progress">
        <div className="hint-tier-dots">
          {[0, 1, 2].map((tier) => (
            <div
              key={tier}
              className={`tier-dot ${tier < hintTier ? 'unlocked' : ''} ${tier === hintTier ? 'current' : ''}`}
            >
              <span className="tier-number">{tier + 1}</span>
            </div>
          ))}
        </div>
        <span className="hint-tier-label">
          {hintTier >= maxTier
            ? 'All hints revealed'
            : `Hint ${hintTier + 1} of ${maxTier}`}
        </span>
      </div>

      {/* Hint descriptions */}
      <div className="hint-descriptions">
        <div className="hint-level">
          <span className="hint-level-tag tag-nudge">Tier 1</span>
          <span className="hint-level-desc">A gentle nudge in the right direction</span>
        </div>
        <div className="hint-level">
          <span className="hint-level-tag tag-technique">Tier 2</span>
          <span className="hint-level-desc">Names the technique you need</span>
        </div>
        <div className="hint-level">
          <span className="hint-level-tag tag-solution">Tier 3</span>
          <span className="hint-level-desc">Near-pseudocode walkthrough</span>
        </div>
      </div>

      {/* Previous hints */}
      {hintComments.length > 0 && (
        <div className="hint-history">
          {hintComments.map((hint, i) => (
            <div key={i} className="hint-item">
              <span className="hint-tier-badge">Tier {i + 1}</span>
              <p className="hint-text">{hint.text.replace('💡 Hint: ', '')}</p>
            </div>
          ))}
        </div>
      )}

      {/* Request button */}
      <button
        className="btn-request-hint"
        onClick={onRequestHint}
        disabled={hintTier >= maxTier}
        id="request-hint-button"
      >
        {hintTier >= maxTier ? '🔓 All Hints Revealed' : `💡 Reveal Hint ${hintTier + 1}`}
      </button>
    </div>
  );
};

export default HintPanel;
