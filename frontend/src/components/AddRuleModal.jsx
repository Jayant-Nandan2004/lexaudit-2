import { RULE_CATEGORIES, RULE_SEVERITIES } from '../constants';

export default function AddRuleModal({ newRule, setNewRule, onSave, onClose }) {
  const update = (field) => (e) => setNewRule({ ...newRule, [field]: e.target.value });

  return (
    <div className="modal-overlay animate-fade-in" onClick={onClose}>
      <div className="glass-panel modal-content" onClick={(e) => e.stopPropagation()} style={{ padding: '24px' }}>
        <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '20px', marginBottom: '16px' }}>
          Create Custom Compliance Rule
        </h3>

        <form onSubmit={onSave}>
          <div className="form-group">
            <label>Rule Title</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="e.g. Mutual Indemnification Cap"
              value={newRule.title}
              onChange={update('title')}
            />
          </div>

          <div className="form-group">
            <label>Compliance Criteria Requirement</label>
            <textarea
              className="form-control"
              rows="4"
              required
              placeholder="e.g. Indemnification obligations must be mutual. Direct IP infringement indemnities must be mutual, and there must be a liability cap..."
              value={newRule.description}
              onChange={update('description')}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group">
              <label>Rule Category</label>
              <select className="form-control" value={newRule.category} onChange={update('category')}>
                {RULE_CATEGORIES.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Violation Severity</label>
              <select className="form-control" value={newRule.severity} onChange={update('severity')}>
                {RULE_SEVERITIES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '12px', marginTop: '16px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Rule
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
