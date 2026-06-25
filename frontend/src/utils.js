// Round a number to a fixed number of decimal places (avoids float artifacts).
export function roundToDecimal(value, decimals) {
  return Number(`${Math.round(`${value}e${decimals}`)}e-${decimals}`);
}

// Split contract text into displayable paragraph blocks.
export function splitParagraphs(text) {
  return (text || '').split('\n\n').filter((p) => p.trim());
}

// Map a compliance score to its themed color variable.
export function scoreColor(score) {
  if (score >= 80) return 'var(--success)';
  if (score >= 50) return 'var(--warning)';
  return 'var(--danger)';
}
