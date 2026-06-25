const SEVERITIES = [
  ['all', 'All Severities'],
  ['Critical', 'Critical'],
  ['Major', 'Major'],
  ['Minor', 'Minor'],
];

const STATUSES = [
  ['all', 'All Status'],
  ['Violations', 'Violations'],
  ['Passed', 'Passed'],
];

function Badge({ active, label, onClick }) {
  return (
    <div className={`filter-badge ${active ? 'active' : ''}`} onClick={onClick}>
      {label}
    </div>
  );
}

export default function FilterBar({ filterSeverity, setFilterSeverity, filterStatus, setFilterStatus }) {
  return (
    <div className="filter-bar">
      {SEVERITIES.map(([value, label]) => (
        <Badge
          key={value}
          active={filterSeverity === value}
          label={label}
          onClick={() => setFilterSeverity(value)}
        />
      ))}

      <div style={{ width: '1px', background: 'var(--border-muted)', height: '20px', margin: '0 4px' }}></div>

      {STATUSES.map(([value, label]) => (
        <Badge
          key={value}
          active={filterStatus === value}
          label={label}
          onClick={() => setFilterStatus(value)}
        />
      ))}
    </div>
  );
}
