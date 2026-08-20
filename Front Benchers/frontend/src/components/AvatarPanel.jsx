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
  neutral_thinking: { label: 'Thinking...', glowClass: 'glow-ember' },
  playful_warning: { label: 'Hmm...', glowClass: 'glow-alert' },
  disappointed: { label: 'Disappointed', glowClass: 'glow-alert' },
  impressed: { label: 'Impressed!', glowClass: 'glow-signal' },
  celebrating: { label: 'Celebrating!', glowClass: 'glow-signal' },
  encouraging: { label: 'Keep going!', glowClass: 'glow-ember' },
};

const AvatarPanel = ({ persona, tone, isAnalyzing }) => {
  const config = PERSONA_CONFIG[persona] || PERSONA_CONFIG.walter_white;
  const toneConfig = TONE_CONFIG[tone] || TONE_CONFIG.neutral_thinking;

  const glowClass = useMemo(() => {
    if (isAnalyzing) return 'glow-ember glow-pulse';
    return toneConfig.glowClass;
  }, [isAnalyzing, toneConfig.glowClass]);

  return (
    <div className="avatar-panel" id="avatar-panel">
      <div className={`avatar-frame ${glowClass}`}>
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
