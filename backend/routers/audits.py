"""Audit endpoints: list/fetch reports and run a compliance audit on a PDF."""

from fastapi import APIRouter, HTTPException, UploadFile, File

import database
import audit_engine

router = APIRouter(prefix="/api", tags=["audits"])

# Maximum accepted upload size (10 MB) — matches the limit advertised in the UI
# and prevents a single large upload from exhausting server memory.
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.get("/audits")
def get_audits():
    return database.get_all_audits()


@router.get("/audits/{audit_id}")
def get_audit(audit_id: str):
    audit_data = database.get_audit(audit_id)
    if not audit_data:
        raise HTTPException(status_code=404, detail="Audit report not found")
    return audit_data


@router.post("/audit")
async def upload_and_audit(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Read uploaded file content with a hard size cap to avoid memory exhaustion.
    contents = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="File too large. Maximum upload size is 10MB.",
        )

    # Basic content sniff: a real PDF starts with the "%PDF-" magic header.
    if not contents.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF.")

    rules = database.get_all_rules()
    if not rules:
        raise HTTPException(
            status_code=400,
            detail="No compliance rules found. Please create rules first.",
        )

    compliance_score, findings, contract_text = audit_engine.run_compliance_audit(contents, rules)

    if not contract_text:
        raise HTTPException(
            status_code=422,
            detail="Could not extract any text from the PDF. It may be empty, scanned, or corrupted.",
        )

    audit_id = database.save_audit(
        filename=file.filename,
        compliance_score=compliance_score,
        contract_text=contract_text,
        findings=findings,
    )
    return database.get_audit(audit_id)
