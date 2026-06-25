import { scoreColor } from '../utils';

const RADIUS = 34;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

// Circular SVG gauge showing the overall compliance score.
export default function ComplianceScore({ score }) {
  const color = scoreColor(score);
  return (
    <div className="circular-score" style={{ border: '2px solid transparent' }}>
      <svg width="80" height="80" style={{ position: 'absolute', transform: 'rotate(-90deg)' }}>
        <circle cx="40" cy="40" r={RADIUS} stroke="rgba(255,255,255,0.05)" strokeWidth="5" fill="transparent" />
        <circle
          cx="40"
          cy="40"
          r={RADIUS}
          stroke={color}
          strokeWidth="5"
          fill="transparent"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={CIRCUMFERENCE * (1 - score / 100)}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.6s ease' }}
        />
      </svg>
      <span style={{ color }}>{score}%</span>
    </div>
  );
}
