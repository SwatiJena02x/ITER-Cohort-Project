import './ProblemSelector.css';

const ProblemSelector = ({ problems, selected, onSelect }) => {
  return (
    <div className="problem-selector" id="problem-selector">
      <select
        value={selected || ''}
        onChange={(e) => onSelect(e.target.value)}
        className="problem-dropdown"
        id="problem-dropdown"
      >
        {problems.map((p) => (
          <option key={p.id} value={p.id}>
            {p.title}
          </option>
        ))}
      </select>
      <span className="dropdown-arrow">▾</span>
    </div>
  );
};

export default ProblemSelector;
