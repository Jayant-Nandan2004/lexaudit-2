import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from reportlab.pdfgen import canvas
import database
import audit_engine

def create_sample_pdf(filepath):
    """Generates a test contract PDF containing compliance violations."""
    print(f"Creating sample contract PDF at: {filepath}")
    c = canvas.Canvas(filepath)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "SERVICES AGREEMENT")
    
    c.setFont("Helvetica", 10)
    y = 710
    
    clauses = [
        "This Agreement is entered into by and between Acme Corp ('Customer') and Globex Solutions ('Contractor').",
        
        "1. SERVICES AND WORK PRODUCT",
        "Contractor shall perform the consulting services detailed in the Statement of Work. Contractor shall own and retain all intellectual property, design models, code scripts, and deliverables created in the course of performing these services. Customer is granted a limited, non-exclusive license to use the deliverables solely for its internal operations.",
        
        "2. MUTUAL INDEMNIFICATION",
        "Customer agrees to defend, indemnify, and hold harmless Contractor, its affiliates, and employees from and against any and all claims, lawsuits, liabilities, or losses arising from the services. Contractor shall have no obligation to defend or indemnify Customer for intellectual property infringement or any other third-party claims.",
        
        "3. GOVERNING LAW",
        "This Agreement and all disputes arising hereunder shall be governed by and construed in accordance with the laws of the State of New York, and the parties agree to submit to the exclusive jurisdiction of the courts located in New York County, New York.",
        
        "4. LIMITATION OF LIABILITY",
        "Customer agrees that Contractor's total aggregate liability for any and all claims, breaches, or damages under this Agreement shall be completely unlimited, and Contractor may claim unlimited damages from Customer. Contractor shall be entitled to recover indirect, special, consequential, and punitive damages from Customer in any dispute, while Customer waives all such claims.",
        
        "5. TERMINATION",
        "Customer may terminate this Agreement only for cause if Contractor fails to cure a material breach within ninety (90) days of receiving written notice. Customer shall have no right to terminate this Agreement for convenience under any circumstances, and any early termination will incur a 50% contract value penalty.",
        
        "6. SECURITY AND DATA BREACH",
        "Contractor will take reasonable administrative precautions. In the event of a security incident or data breach, Contractor will notify Customer of such breach within thirty (30) days of discovering the incident."
    ]
    
    for clause in clauses:
        # Simple word wrapping for PDF generation
        words = clause.split(' ')
        line = ""
        for word in words:
            if len(line + " " + word) * 5 < 450:
                line += " " + word
            else:
                c.drawString(80, y, line.strip())
                y -= 15
                line = word
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = 750
        if line:
            c.drawString(80, y, line.strip())
            y -= 25 # double spacing between paragraphs
            
    c.save()
    print("Sample PDF contract created successfully.")

def run_test():
    # Initialize DB
    print("Initializing Database...")
    database.init_db()
    
    # The audit engine runs fully offline (no API key required).
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_contract.pdf")
    create_sample_pdf(pdf_path)
    
    # Read PDF stream
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
        
    print("\nStarting Offline Compliance Scan...")
    rules = database.get_all_rules()

    try:
        compliance_score, findings, text = audit_engine.run_compliance_audit(pdf_bytes, rules)
        
        print("\n=======================================================")
        print(f"AUDIT COMPLETED | Compliance Score: {compliance_score}%")
        print("=======================================================")
        
        for f in findings:
            status = "PASSED" if f["compliant"] else "FAILED"
            print(f"\n[{status}] - Rule: {f['rule_title']} ({f['rule_severity']})")
            print(f"  Reasoning: {f['reasoning']}")
            if f["matched_text"]:
                print(f"  Matched Text: '{f['matched_text']}'")
            if f["correction"]:
                print(f"  Suggested Correction: '{f['correction']}'")
                
    except Exception as e:
        print(f"\n[ERROR] Audit execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
