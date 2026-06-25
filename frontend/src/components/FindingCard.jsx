import { IconCheck } from './Icons';

// Derive the status chip class/label from a finding's compliance flags.
function statusOf(finding) {
  if (!finding.clause_found) return { cls: 'missing', label: 'Missing Clause' };
  if (!finding.compliant) return { cls: 'failed', label: 'Violation' };
  return { cls: 'passed', label: 'Passed' };
}

export default function FindingCard({ finding, isExpanded, onClick, onApplyCorrection }) {
  const status = statusOf(finding);

  return (
    <div
      className={`finding-card ${status.cls} ${isExpanded ? 'active' : ''}`}
      onClick={() => onClick(finding)}
    >
      <div className="card-header">
        <div>
          <span className={`badge badge-${finding.rule_severity.toLowerCase()}`} style={{ marginRight: '8px' }}>
            {finding.rule_severity}
          </span>
          <span className={`badge badge-${status.cls}`}>{status.label}</span>
          <h4 className="finding-title" style={{ marginTop: '6px' }}>
            {finding.rule_title}
          </h4>
        </div>
        <span>{finding.rule_category}</span>
      </div>
      <p className="finding-reasoning">{finding.reasoning}</p>

      {isExpanded && !finding.compliant && (
        <div className="diff-container animate-fade-in" onClick={(e) => e.stopPropagation()}>
          {finding.matched_text && (
            <div className="diff-section diff-removed">
              <strong>CURRENT CLAUSE:</strong>
              <p>{finding.matched_text}</p>
            </div>
          )}
          {finding.correction && (
            <div className="diff-section diff-added">
              <strong>SUGGESTED CORRECTION:</strong>
              <p>{finding.correction}</p>
            </div>
          )}
          {finding.correction && (
            <button className="apply-btn" onClick={() => onApplyCorrection(finding)}>
              <IconCheck />
              Apply Correction
            </button>
          )}
        </div>
      )}
    </div>
  );
}
