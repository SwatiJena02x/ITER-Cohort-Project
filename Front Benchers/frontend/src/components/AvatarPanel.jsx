import { useMemo } from 'react';
import './AvatarPanel.css';

const PERSONA_CONFIG = {
  walter_white: {
    name: 'Walter White',
    emoji: '🧪',
    color: '#4CAF50',
    subtitle: 'Chemistry Teacher',
  },
  kratos: {
    name: 'Kratos',
    emoji: '⚔️',
    color: '#E53935',
    subtitle: 'God of War',
  },
  thanos: {
    name: 'Thanos',
    emoji: '💎',
    color: '#7E57C2',
    subtitle: 'The Mad Titan',
  },
};

const TONE_CONFIG = {
  neutral_thinking: { label: 'Thinking...', frameClass: 'tone-ember' },
  playful_warning: { label: 'Hmm...', frameClass: 'tone-alert' },
  disappointed: { label: 'Disappointed', frameClass: 'tone-alert' },
  impressed: { label: 'Impressed!', frameClass: 'tone-signal' },
  celebrating: { label: 'Celebrating!', frameClass: 'tone-signal' },
  encouraging: { label: 'Keep going!', frameClass: 'tone-spark' },
};

const AvatarPanel = ({ persona, tone, isAnalyzing }) => {
  const config = PERSONA_CONFIG[persona] || PERSONA_CONFIG.walter_white;
  const toneConfig = TONE_CONFIG[tone] || TONE_CONFIG.neutral_thinking;

  const frameClass = useMemo(() => {
    if (isAnalyzing) return 'tone-ember analyzing-pulse';
    return toneConfig.frameClass;
  }, [isAnalyzing, toneConfig.frameClass]);

  return (
    <div className="avatar-panel" id="avatar-panel">
      <div className={`avatar-frame ${frameClass}`}>
        <div className="avatar-inner" style={{ '--persona-color': config.color }}>
          <span className="avatar-emoji">{config.emoji}</span>
        </div>
      </div>
      <div className="avatar-info">
        <h3 className="avatar-name">{config.name}</h3>
        <span className="avatar-subtitle">{config.subtitle}</span>
        <span className={`avatar-tone tone-${tone}`}>
          {isAnalyzing ? '⏳ Analyzing...' : toneConfig.label}
        </span>
      </div>
    </div>
  );
};

export default AvatarPanel;
