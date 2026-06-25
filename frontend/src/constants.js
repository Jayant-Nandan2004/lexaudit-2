// Backend API base. Defaults to the local FastAPI server on port 8000; override
// at build/dev time with VITE_API_BASE (e.g. if port 8000 is already in use).
export const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000/api';

// Animated steps shown while an audit runs. The final API response completes them.
export const LOADING_STEPS = [
  { id: 1, label: 'Uploading PDF document...' },
  { id: 2, label: 'Extracting pages & paragraph boundaries...' },
  { id: 3, label: 'Generating document chunks & keyword index...' },
  { id: 4, label: 'Retrieving relevant clauses for each policy rule...' },
  { id: 5, label: 'Auditing clauses & drafting compliant corrections...' },
];

export const RULE_CATEGORIES = [
  'Liability',
  'Indemnity',
  'Intellectual Property',
  'Compliance',
  'Termination',
  'General',
];

export const RULE_SEVERITIES = ['Critical', 'Major', 'Minor'];
