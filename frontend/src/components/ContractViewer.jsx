import { useRef } from 'react';
import { IconDocument, IconUpload } from './Icons';
import AuditLoader from './AuditLoader';

// Left pane: upload dropzone, animated loader, or the interactive contract draft.
export default function ContractViewer({
  isAuditing,
  loadingSteps,
  selectedAudit,
  contractParagraphs,
  selectedFindingId,
  getParagraphViolation,
  onFindingClick,
  onFileUpload,
}) {
  const fileInputRef = useRef(null);

  return (
    <div className="glass-panel viewer-panel animate-fade-in">
      <div className="panel-header">
        <span className="panel-title">
          <IconDocument />
          Contract Document Workspace
        </span>
        {selectedAudit && (
          <span style={{ fontSize: '12px', color: 'var(--text-dim)' }}>
            File: <strong>{selectedAudit.filename}</strong>
          </span>
        )}
      </div>
      <div className="panel-body">
        {isAuditing ? (
          <AuditLoader steps={loadingSteps} />
        ) : selectedAudit ? (
          <div className="contract-editor">
            {contractParagraphs.map((para, index) => {
              const violation = getParagraphViolation(para);
              const isHighlighted = violation && selectedFindingId === violation.id;

              let className = 'contract-paragraph';
              if (violation) className += ' violation';
              if (isHighlighted) className += ' active';

              return (
                <div
                  key={index}
                  id={`p-${index}`}
                  className={className}
                  onClick={() => violation && onFindingClick(violation)}
                  style={{ cursor: violation ? 'pointer' : 'default' }}
                >
                  {para}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="upload-dropzone animate-fade-in" onClick={() => fileInputRef.current?.click()}>
            <div className="upload-icon">
              <IconUpload />
            </div>
            <div>
              <h3 style={{ fontFamily: 'var(--font-title)', fontSize: '18px', marginBottom: '6px' }}>
                Upload Contract for Audit
              </h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Supports contract PDFs up to 10MB</p>
            </div>
            <button className="btn btn-primary" style={{ marginTop: '8px' }}>
              Select File
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={onFileUpload}
              accept=".pdf"
              style={{ display: 'none' }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
