import './PersonaSelector.css';

const PERSONAS = [
  { key: 'walter_white', name: 'Walter White', emoji: '🧪' },
  { key: 'kratos', name: 'Kratos', emoji: '⚔️' },
  { key: 'thanos', name: 'Thanos', emoji: '💎' },
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
        >
          <span className="persona-emoji">{p.emoji}</span>
          <span className="persona-name">{p.name}</span>
        </button>
      ))}
    </div>
  );
};

export default PersonaSelector;
