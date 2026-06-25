import { IconClock, IconChevronRight } from './Icons';
import { scoreColor } from '../utils';

function HistoryCard({ item, onSelect }) {
  return (
    <div className="history-card" onClick={() => onSelect(item.id)}>
      <div className="history-info">
        <span className="history-filename">{item.filename}</span>
        <span className="history-date">Scanned on {new Date(item.timestamp).toLocaleString()}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span style={{ fontWeight: 700, fontSize: '18px', color: scoreColor(item.compliance_score) }}>
          {item.compliance_score}%
        </span>
        <IconChevronRight style={{ color: 'var(--text-dim)' }} />
      </div>
    </div>
  );
}

export default function HistoryPanel({ audits, onSelectAudit }) {
  return (
    <div className="glass-panel viewer-panel animate-fade-in" style={{ gridColumn: '1 / -1' }}>
      <div className="panel-header">
        <span className="panel-title">
          <IconClock />
          Audit History Logs
        </span>
      </div>

      <div className="panel-body" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
        {audits.length > 0 ? (
          <div className="history-list">
            {audits.map((item) => (
              <HistoryCard key={item.id} item={item} onSelect={onSelectAudit} />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '48px', color: 'var(--text-dim)' }}>
            No historical audits found. Go to the Auditor IDE to run your first check.
          </div>
        )}
      </div>
    </div>
  );
}
