const TABS = [
  { key: 'audit', label: () => 'Auditor IDE' },
  { key: 'rules', label: (counts) => `Policy Rules (${counts.rules})` },
  { key: 'history', label: (counts) => `Audit History (${counts.audits})` },
];

export default function Header({ activeTab, setActiveTab, rulesCount, auditsCount }) {
  const counts = { rules: rulesCount, audits: auditsCount };
  return (
    <header className="glass-panel app-header animate-fade-in">
      <div className="logo-container">
        <div className="logo-icon">L</div>
        <span className="logo-text">LexAudit AI</span>
      </div>
      <div className="header-actions">
        <div className="tabs-container">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.key)}
            >
              {tab.label(counts)}
            </button>
          ))}
        </div>
      </div>
    </header>
  );
}
