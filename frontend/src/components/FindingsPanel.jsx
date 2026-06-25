import { IconShieldCheck, IconInfoCircle } from './Icons';
import ComplianceScore from './ComplianceScore';
import FilterBar from './FilterBar';
import FindingCard from './FindingCard';

// Right pane: compliance score, filters, and the list of findings.
export default function FindingsPanel({
  selectedAudit,
  filteredFindings,
  selectedFindingId,
  filterSeverity,
  setFilterSeverity,
  filterStatus,
  setFilterStatus,
  onFindingClick,
  onApplyCorrection,
}) {
  return (
    <div className="glass-panel viewer-panel animate-fade-in">
      <div className="panel-header">
        <span className="panel-title">
          <IconShieldCheck />
          Compliance Findings
        </span>
        {selectedAudit && <ComplianceScore score={selectedAudit.compliance_score} />}
      </div>
      <div className="panel-body">
        {selectedAudit ? (
          <>
            <FilterBar
              filterSeverity={filterSeverity}
              setFilterSeverity={setFilterSeverity}
              filterStatus={filterStatus}
              setFilterStatus={setFilterStatus}
            />

            <div className="findings-list">
              {filteredFindings.length > 0 ? (
                filteredFindings.map((finding) => (
                  <FindingCard
                    key={finding.id}
                    finding={finding}
                    isExpanded={selectedFindingId === finding.id}
                    onClick={onFindingClick}
                    onApplyCorrection={onApplyCorrection}
                  />
                ))
              ) : (
                <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-dim)' }}>
                  No compliance findings match the current filters.
                </div>
              )}
            </div>
          </>
        ) : (
          <div
            style={{
              height: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-dim)',
              textAlign: 'center',
              padding: '24px',
            }}
          >
            <div>
              <IconInfoCircle style={{ marginBottom: '12px' }} />
              <p>Upload a contract PDF in the Workspace pane to launch the audit scans.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
