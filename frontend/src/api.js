import { API_BASE } from './constants';

// Parse a fetch Response: return JSON on success, throw an Error carrying the
// backend's `detail` message (and status) on failure.
async function handle(res) {
  if (res.ok) {
    return res.status === 204 ? null : res.json();
  }
  let detail = 'Unknown error';
  try {
    const body = await res.json();
    detail = body.detail || detail;
  } catch {
    /* response had no JSON body */
  }
  const err = new Error(detail);
  err.status = res.status;
  throw err;
}

export const getRules = () => fetch(`${API_BASE}/rules`).then(handle);

export const createRule = (rule) =>
  fetch(`${API_BASE}/rules`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(rule),
  }).then(handle);

export const deleteRule = (ruleId) =>
  fetch(`${API_BASE}/rules/${ruleId}`, { method: 'DELETE' }).then(handle);

export const getAudits = () => fetch(`${API_BASE}/audits`).then(handle);

export const getAudit = (auditId) => fetch(`${API_BASE}/audits/${auditId}`).then(handle);

export const uploadAudit = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return fetch(`${API_BASE}/audit`, { method: 'POST', body: formData }).then(handle);
};
