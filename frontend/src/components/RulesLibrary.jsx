import { IconBook } from './Icons';

function RuleCard({ rule, onDelete }) {
  return (
    <div
      className="glass-panel"
      style={{ padding: '20px', display: 'flex', flexDirection: 'column', justifyContent: 'between', gap: '12px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
        <span className={`badge badge-${rule.severity.toLowerCase()}`}>{rule.severity}</span>
        <span style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-dim)' }}>
          {rule.category}
        </span>
      </div>
      <div style={{ flex: 1 }}>
        <h4
          style={{
            fontFamily: 'var(--font-title)',
            fontWeight: 700,
            fontSize: '16px',
            marginBottom: '8px',
            color: 'var(--text-main)',
          }}
        >
          {rule.title}
        </h4>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5' }}>{rule.description}</p>
      </div>

      {!rule.is_default && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            borderTop: '1px solid var(--border-muted)',
            paddingTop: '10px',
          }}
        >
          <button
            className="btn btn-secondary"
            onClick={() => onDelete(rule.id)}
            style={{ padding: '6px 12px', fontSize: '12px', color: 'var(--danger)', borderColor: 'rgba(239, 68, 68, 0.2)' }}
          >
            Delete Rule
          </button>
        </div>
      )}
    </div>
  );
}

export default function RulesLibrary({ rules, onAddRule, onDeleteRule }) {
  return (
    <div className="glass-panel viewer-panel animate-fade-in" style={{ gridColumn: '1 / -1' }}>
      <div className="panel-header">
        <span className="panel-title">
          <IconBook />
          Compliance Rules Policy Library
        </span>
        <button className="btn btn-primary" onClick={onAddRule}>
          + Create Custom Rule
        </button>
      </div>

      <div className="panel-body">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {rules.map((rule) => (
            <RuleCard key={rule.id} rule={rule} onDelete={onDeleteRule} />
          ))}
        </div>
      </div>
    </div>
  );
}
