import sqlite3
import os
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexaudit.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Create rules table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                is_default BOOLEAN DEFAULT 0
            )
        """)
        
        # Create audits table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                compliance_score REAL NOT NULL,
                contract_text TEXT
            )
        """)
        
        # Create audit_results table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audit_id TEXT NOT NULL,
                rule_id INTEGER,
                rule_title TEXT NOT NULL,
                rule_category TEXT NOT NULL,
                rule_severity TEXT NOT NULL,
                compliant BOOLEAN NOT NULL,
                clause_found BOOLEAN NOT NULL,
                matched_text TEXT,
                reasoning TEXT,
                correction TEXT,
                FOREIGN KEY (audit_id) REFERENCES audits (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
    
    # Seed default rules
    seed_default_rules()

def seed_default_rules():
    default_rules = [
        {
            "title": "Limitation of Liability Caps",
            "description": "Liability caps must be reasonable (e.g., capped at fees paid in the trailing 12 months) and must explicitly exclude indirect, incidental, special, or consequential damages.",
            "category": "Liability",
            "severity": "Critical"
        },
        {
            "title": "Mutual Indemnification",
            "description": "Indemnification obligations must be mutual. Avoid one-sided obligations where the company indemnifies the provider but receives no counter-indemnification for intellectual property infringement or data breaches.",
            "category": "Indemnity",
            "severity": "Major"
        },
        {
            "title": "Governing Law and Jurisdiction",
            "description": "Governing law must be California or Delaware, and the venue for disputes must be courts located in those respective states.",
            "category": "General",
            "severity": "Minor"
        },
        {
            "title": "Intellectual Property Ownership",
            "description": "All intellectual property, deliverables, and works created by a contractor or service provider during the engagement must be assigned to and owned by the Customer as 'work made for hire'.",
            "category": "Intellectual Property",
            "severity": "Critical"
        },
        {
            "title": "Data Privacy and Breach Notification",
            "description": "The contract must include compliance with applicable data privacy laws (GDPR, CCPA) and mandate that the vendor notify the company of any data security breach within 72 hours of discovery.",
            "category": "Compliance",
            "severity": "Critical"
        },
        {
            "title": "Termination for Convenience",
            "description": "The contract must allow the customer to terminate the agreement for convenience (without cause) upon no more than 30 days written notice, without penalty.",
            "category": "Termination",
            "severity": "Major"
        }
    ]
    
    with get_db() as conn:
        for r in default_rules:
            try:
                conn.execute(
                    "INSERT INTO rules (title, description, category, severity, is_default) VALUES (?, ?, ?, ?, 1)",
                    (r["title"], r["description"], r["category"], r["severity"])
                )
            except sqlite3.IntegrityError:
                # Already exists
                pass
        conn.commit()

# Rule Operations
def get_all_rules():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM rules ORDER BY category, title").fetchall()
        return [dict(r) for r in rows]

def get_rule(rule_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM rules WHERE id = ?", (rule_id,)).fetchone()
        return dict(row) if row else None

def create_rule(title: str, description: str, category: str, severity: str):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rules (title, description, category, severity, is_default) VALUES (?, ?, ?, ?, 0)",
            (title, description, category, severity)
        )
        conn.commit()
        return cursor.lastrowid

def update_rule(rule_id: int, title: str, description: str, category: str, severity: str):
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE rules SET title = ?, description = ?, category = ?, severity = ? WHERE id = ?",
            (title, description, category, severity, rule_id)
        )
        conn.commit()
        return cursor.rowcount > 0

def delete_rule(rule_id: int):
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        conn.commit()
        return cursor.rowcount > 0

# Audit Operations
def save_audit(filename: str, compliance_score: float, contract_text: str, findings: list):
    audit_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    with get_db() as conn:
        conn.execute(
            "INSERT INTO audits (id, filename, timestamp, compliance_score, contract_text) VALUES (?, ?, ?, ?, ?)",
            (audit_id, filename, timestamp, compliance_score, contract_text)
        )
        
        for f in findings:
            conn.execute("""
                INSERT INTO audit_results (
                    audit_id, rule_id, rule_title, rule_category, rule_severity, 
                    compliant, clause_found, matched_text, reasoning, correction
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_id,
                f.get("rule_id"),
                f["rule_title"],
                f["rule_category"],
                f["rule_severity"],
                f["compliant"],
                f["clause_found"],
                f.get("matched_text"),
                f.get("reasoning"),
                f.get("correction")
            ))
        conn.commit()
    return audit_id

def get_all_audits():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM audits ORDER BY timestamp DESC").fetchall()
        return [dict(r) for r in rows]

def get_audit(audit_id: str):
    with get_db() as conn:
        audit = conn.execute("SELECT * FROM audits WHERE id = ?", (audit_id,)).fetchone()
        if not audit:
            return None
        
        results = conn.execute("SELECT * FROM audit_results WHERE audit_id = ?", (audit_id,)).fetchall()
        
        return {
            **dict(audit),
            "findings": [dict(r) for r in results]
        }
