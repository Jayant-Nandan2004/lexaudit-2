"""Offline contract compliance audit engine.

This module runs the full audit pipeline (PDF text extraction -> chunking ->
keyword retrieval -> heuristic clause analysis) without any external API or
network access. It deliberately has no dependency on a Gemini/LLM key: clause
detection and compliance decisions are made by deterministic keyword/regex
matchers, so the app works fully offline.

Public entry point: ``run_compliance_audit(pdf_bytes, rules)``.
"""

import io
import re
from pypdf import PdfReader

# A small English stop-word list used for keyword scoring during retrieval.
_STOP_WORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "at", "by",
    "with", "is", "are", "be", "as", "that", "this", "it", "its", "any", "all",
    "must", "shall", "will", "not", "no", "such", "from", "which", "their",
    "they", "than", "then", "into", "within", "upon", "may", "if", "each",
    "other", "there", "where", "these", "those", "have", "has",
}

# Section divider inserted between retrieved chunks when building rule context.
_DIVIDER = "\n\n--- NEXT RELEVANT SECTION ---\n\n"


# ---------------------------------------------------------------------------
# PDF extraction & chunking
# ---------------------------------------------------------------------------
def _normalize_paragraphs(text: str) -> str:
    """Reflow extracted lines into logical paragraphs.

    Many PDFs extract as one visual line per ``\\n`` with no blank-line breaks
    between clauses. We rebuild paragraphs by joining wrapped lines and starting
    a new paragraph at blank lines or numbered section headings (e.g. "3. ...").
    """
    paragraphs, current = [], []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        # A numbered section heading starts a fresh paragraph.
        if current and re.match(r"^\d+\.\s+\S", line):
            paragraphs.append(" ".join(current))
            current = []
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))
    return "\n\n".join(paragraphs)


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text content page by page from raw PDF bytes."""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text_pages = [page.extract_text() for page in reader.pages]
        raw = "\n".join(p for p in text_pages if p)
        return _normalize_paragraphs(raw)
    except Exception as e:  # pragma: no cover - corrupt/encrypted PDFs
        print(f"Error parsing PDF: {e}")
        return ""


def chunk_text(text: str, max_chunk_size: int = 1200, overlap: int = 200) -> list:
    """Split document text into overlapping paragraph-based chunks.

    Paragraphs are accumulated until ``max_chunk_size`` is reached. To preserve
    context across boundaries, the tail paragraphs of the previous chunk (up to
    ``overlap`` characters) are carried into the next chunk.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return []

    chunks = []
    current = []
    current_len = 0

    def _overlap_tail(paras):
        """Return trailing paragraphs of ``paras`` fitting within ``overlap``."""
        tail, length = [], 0
        for p in reversed(paras):
            if length + len(p) > overlap:
                break
            tail.insert(0, p)
            length += len(p) + 2
        return tail

    for p in paragraphs:
        if current and current_len + len(p) > max_chunk_size:
            chunks.append("\n\n".join(current))
            current = _overlap_tail(current)
            current_len = sum(len(x) + 2 for x in current)
        current.append(p)
        current_len += len(p) + 2

    if current:
        chunks.append("\n\n".join(current))

    return chunks


# ---------------------------------------------------------------------------
# Keyword retrieval (local, no embeddings)
# ---------------------------------------------------------------------------
def _tokenize(text: str) -> list:
    """Lowercase word tokens with stop-words removed."""
    words = re.findall(r"[a-z][a-z']+", text.lower())
    return [w for w in words if w not in _STOP_WORDS and len(w) > 2]


def score_chunk(query_tokens: set, chunk_tokens: list) -> float:
    """Score a chunk by how many distinct query keywords it contains."""
    if not query_tokens or not chunk_tokens:
        return 0.0
    chunk_set = set(chunk_tokens)
    hits = sum(1 for t in query_tokens if t in chunk_set)
    return hits / len(query_tokens)


def retrieve_relevant_chunks(rule_description: str, scored_chunks: list, top_k: int = 3) -> str:
    """Return the ``top_k`` chunks most relevant to ``rule_description``.

    ``scored_chunks`` is a list of ``(chunk_text, chunk_tokens)`` tuples, prepared
    once per document by :func:`run_compliance_audit`.
    """
    query_tokens = set(_tokenize(rule_description))
    ranked = sorted(
        scored_chunks,
        key=lambda c: score_chunk(query_tokens, c[1]),
        reverse=True,
    )
    relevant = [chunk for chunk, _ in ranked[:top_k]]
    return _DIVIDER.join(relevant)


# ---------------------------------------------------------------------------
# Heuristic clause matchers
# ---------------------------------------------------------------------------
# Each matcher describes how to detect and evaluate one class of clause:
#   select     - keywords; if present in the rule title/description this matcher
#                is chosen for that rule.
#   topic      - regexes indicating the clause topic is present in the contract.
#   violation  - regexes that, when matched, mark the clause non-compliant.
#   require    - regexes of which at least one MUST be present to be compliant
#                (used for "must be X" rules, e.g. governing law = CA/DE).
#   correction - a compliant drop-in replacement clause.
_MATCHERS = [
    {
        "key": "liability_cap",
        "select": ["liability", "limitation of liability", "consequential", "damages cap"],
        "topic": [r"limitation of liability", r"aggregate liability", r"liabilit"],
        "violation": [
            r"unlimited", r"no\s+cap\b", r"recover\s+indirect",
            r"consequential,?\s+and\s+punitive", r"punitive damages from",
        ],
        "compliant": [r"shall not exceed", r"fees paid", r"trailing\s+(?:twelve|12)"],
        "correction": (
            "Each party's total aggregate liability arising out of or related to "
            "this Agreement shall not exceed the total fees paid in the trailing "
            "twelve (12) months. In no event shall either party be liable for "
            "indirect, incidental, special, or consequential damages."
        ),
    },
    {
        "key": "mutual_indemnification",
        "select": ["indemnif", "indemnity", "hold harmless"],
        "topic": [r"indemnif", r"hold harmless"],
        "violation": [
            r"no obligation to (?:defend|indemnify)",
            r"shall have no obligation",
            r"one-sided",
        ],
        "compliant": [r"\bmutual", r"each party shall (?:defend|indemnify)"],
        "correction": (
            "Each party shall defend, indemnify, and hold harmless the other "
            "party from and against any third-party claims arising from its own "
            "negligence, breach, or infringement of intellectual property rights, "
            "on a mutual and reciprocal basis."
        ),
    },
    {
        "key": "governing_law",
        "select": ["governing law", "jurisdiction", "venue", "dispute"],
        "topic": [r"governed by", r"governing law", r"jurisdiction", r"\bvenue\b"],
        "violation": [],
        "require": [r"california", r"delaware"],
        "correction": (
            "This Agreement shall be governed by and construed in accordance with "
            "the laws of the State of Delaware, and the parties submit to the "
            "exclusive jurisdiction of the state and federal courts located in "
            "Delaware."
        ),
    },
    {
        "key": "ip_ownership",
        "select": ["intellectual property", "work product", "deliverables", "work made for hire"],
        "topic": [r"intellectual property", r"deliverables", r"work product", r"work made for hire"],
        "violation": [
            r"contractor shall own", r"provider shall own",
            r"(?:contractor|provider|vendor) (?:shall|will) (?:own|retain)",
        ],
        "compliant": [r"work made for hire", r"assigned to (?:the )?customer", r"customer (?:shall )?own"],
        "correction": (
            "All intellectual property, deliverables, and works created by the "
            "Contractor in the course of the engagement shall be deemed 'work "
            "made for hire' and are hereby assigned to and owned exclusively by "
            "the Customer."
        ),
    },
    {
        "key": "data_privacy_breach",
        "select": ["data privacy", "breach notification", "gdpr", "ccpa", "data security", "personal data"],
        "topic": [r"data breach", r"security (?:incident|breach)", r"\bbreach\b", r"data privacy", r"personal data"],
        "violation": [],
        "require": [r"72\s*hours", r"seventy-two\s*\(?72\)?\s*hours"],
        "correction": (
            "Vendor shall comply with all applicable data privacy laws (including "
            "GDPR and CCPA) and shall notify the Company of any data security "
            "breach within seventy-two (72) hours of discovery."
        ),
    },
    {
        "key": "termination_for_convenience",
        "select": ["termination", "terminate", "convenience"],
        "topic": [r"terminat"],
        "violation": [
            r"no right to terminate", r"only for cause",
            r"\bpenalty\b", r"may not terminate",
        ],
        "compliant": [r"terminate (?:this agreement )?for convenience", r"without cause"],
        "correction": (
            "The Customer may terminate this Agreement for convenience, without "
            "cause and without penalty, upon thirty (30) days' prior written "
            "notice to the Contractor."
        ),
    },
]


def _compile(patterns: list):
    return [re.compile(p, re.IGNORECASE) for p in patterns]


# Pre-compile all matcher regexes once at import time.
for _m in _MATCHERS:
    _m["_topic"] = _compile(_m.get("topic", []))
    _m["_violation"] = _compile(_m.get("violation", []))
    _m["_require"] = _compile(_m.get("require", []))
    _m["_compliant"] = _compile(_m.get("compliant", []))


def _select_matcher(rule: dict):
    """Pick the matcher whose ``select`` keywords best fit the rule text."""
    haystack = f"{rule.get('title', '')} {rule.get('description', '')}".lower()
    best, best_hits = None, 0
    for m in _MATCHERS:
        hits = sum(1 for kw in m["select"] if kw in haystack)
        if hits > best_hits:
            best, best_hits = m, hits
    return best


def _find_paragraph(context_text: str, regexes: list) -> str:
    """Return the sentence within context matched by any regex (substring-safe).

    The returned text is always a contiguous substring of a contract paragraph,
    so the frontend can locate and highlight it precisely.
    """
    segments = [
        s.strip()
        for s in context_text.split("\n\n")
        if s.strip() and not s.strip().startswith("--- NEXT RELEVANT SECTION")
    ]
    # Try the most specific (earliest-listed) pattern across all segments first,
    # so a generic fallback pattern doesn't win over a precise one elsewhere.
    for rx in regexes:
        for seg in segments:
            if not rx.search(seg):
                continue
            # Narrow the match down to the enclosing sentence for precision.
            for sentence in re.split(r"(?<=[.;])\s+", seg):
                if rx.search(sentence):
                    return sentence.strip()
            return seg
    return ""


def audit_clause_against_rule(rule: dict, context_text: str) -> dict:
    """Evaluate retrieved contract context against a single compliance rule.

    Returns a dict with the same shape the rest of the app expects:
    ``clause_found``, ``compliant``, ``matched_text``, ``reasoning``, ``correction``.
    """
    matcher = _select_matcher(rule)

    if matcher is None:
        return _generic_audit(rule, context_text)

    clause_found = any(rx.search(context_text) for rx in matcher["_topic"])
    if not clause_found:
        return {
            "clause_found": False,
            "compliant": False,
            "matched_text": "",
            "reasoning": (
                f"No clause addressing '{rule['title']}' was found in the "
                "contract. This requirement is unmet."
            ),
            "correction": matcher["correction"],
        }

    has_violation = any(rx.search(context_text) for rx in matcher["_violation"])
    missing_required = bool(matcher["_require"]) and not any(
        rx.search(context_text) for rx in matcher["_require"]
    )
    compliant = not has_violation and not missing_required

    if compliant:
        matched = _find_paragraph(
            context_text, matcher["_compliant"] or matcher["_topic"]
        )
        return {
            "clause_found": True,
            "compliant": True,
            "matched_text": matched,
            "reasoning": (
                f"A clause addressing '{rule['title']}' was found and appears to "
                "satisfy the requirement. No violating language was detected."
            ),
            "correction": "",
        }

    matched = _find_paragraph(
        context_text, matcher["_violation"] or matcher["_topic"]
    )
    if missing_required:
        reasoning = (
            f"A clause addressing '{rule['title']}' was found, but it does not "
            "meet the required condition stated in the rule. "
        )
    else:
        reasoning = (
            f"The clause addressing '{rule['title']}' contains language that "
            "violates the rule requirement. "
        )
    reasoning += "A compliant replacement is suggested below."

    return {
        "clause_found": True,
        "compliant": False,
        "matched_text": matched,
        "reasoning": reasoning,
        "correction": matcher["correction"],
    }


def _generic_audit(rule: dict, context_text: str) -> dict:
    """Fallback for custom rules with no dedicated matcher.

    Detects clause presence via keyword overlap; since intent cannot be verified
    heuristically, a present clause is treated as compliant and an absent one as
    a missing-clause finding.
    """
    query_tokens = set(_tokenize(rule.get("description", "")))
    context_tokens = set(_tokenize(context_text))
    hits = query_tokens & context_tokens
    clause_found = len(hits) >= 2

    if clause_found:
        return {
            "clause_found": True,
            "compliant": True,
            "matched_text": _find_paragraph(
                context_text, [re.compile(re.escape(w), re.IGNORECASE) for w in hits]
            ),
            "reasoning": (
                f"A clause relevant to '{rule['title']}' was located based on "
                "matching terminology. Manual legal review is recommended to "
                "confirm full compliance."
            ),
            "correction": "",
        }

    return {
        "clause_found": False,
        "compliant": False,
        "matched_text": "",
        "reasoning": (
            f"No clause addressing '{rule['title']}' could be located in the "
            "contract. Consider inserting a clause that satisfies this rule."
        ),
        "correction": f"Insert a clause that satisfies the requirement: {rule.get('description', '')}",
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_compliance_audit(pdf_bytes: bytes, rules: list) -> tuple:
    """Run a full offline compliance audit on a PDF against a list of rules.

    Returns ``(compliance_score, findings, full_text)``.
    """
    full_text = extract_text_from_pdf(pdf_bytes)
    if not full_text:
        return 0.0, [], ""

    chunks = chunk_text(full_text)
    scored_chunks = [(chunk, _tokenize(chunk)) for chunk in chunks]

    findings = []
    passed_count = 0

    for rule in rules:
        context = retrieve_relevant_chunks(rule["description"], scored_chunks)
        result = audit_clause_against_rule(rule, context)

        finding = {
            "rule_id": rule["id"],
            "rule_title": rule["title"],
            "rule_category": rule["category"],
            "rule_severity": rule["severity"],
            "compliant": result.get("compliant", False),
            "clause_found": result.get("clause_found", False),
            "matched_text": result.get("matched_text", ""),
            "reasoning": result.get("reasoning", ""),
            "correction": result.get("correction", ""),
        }
        findings.append(finding)
        if finding["compliant"]:
            passed_count += 1

    total_rules = len(rules)
    compliance_score = round((passed_count / total_rules) * 100, 1) if total_rules else 100.0

    return compliance_score, findings, full_text
