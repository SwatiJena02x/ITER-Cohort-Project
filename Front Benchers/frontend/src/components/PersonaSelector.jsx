import './PersonaSelector.css';

const PERSONAS = [
  { key: 'walter_white', name: 'Walter White', emoji: '🧪', color: '#4CAF50' },
  { key: 'kratos', name: 'Kratos', emoji: '⚔️', color: '#E53935' },
  { key: 'thanos', name: 'Thanos', emoji: '💎', color: '#9B87F5' },
];

const PersonaSelector = ({ selected, onSelect }) => {
  return (
    <div className="persona-selector" id="persona-selector">
      {PERSONAS.map((p) => (
        <button
          key={p.key}
          className={`persona-btn ${selected === p.key ? 'active' : ''}`}
          onClick={() => onSelect(p.key)}
          title={p.name}
          id={`persona-${p.key}`}
          style={{ '--persona-accent': p.color }}
        >
          <span className="persona-emoji">{p.emoji}</span>
          <span className="persona-name">{p.name}</span>
        </button>
      ))}
    </div>
  );
};

export default PersonaSelector;
