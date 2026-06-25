export default function AuditLoader({ steps }) {
  return (
    <div className="loader-container">
      <div className="loader-spinner"></div>
      <div style={{ textAlign: 'center' }}>
        <h3 style={{ fontFamily: 'var(--font-title)', marginBottom: '8px' }}>
          Compliance Pipeline Processing
        </h3>
        <p style={{ color: 'var(--text-dim)', fontSize: '13px' }}>
          Analyzing document clauses against the policy library
        </p>
      </div>
      <div className="loader-steps">
        {steps.map((step) => (
          <div key={step.id} className={`loader-step ${step.status}`}>
            <div className="step-indicator"></div>
            <span>{step.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
