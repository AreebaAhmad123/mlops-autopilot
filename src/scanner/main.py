# scanner/main.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from scanner import MLOPSScanner
from audit.engine import MLOpsAuditEngine
from audit.report import ReportBuilder
import uvicorn
import traceback

app = FastAPI(title="MLOps Autopilot Scanner")
scanner = MLOPSScanner()
audit_engine = MLOpsAuditEngine()
report_builder = ReportBuilder()

class ScanRequest(BaseModel):
    repo_url: str

@app.post("/audit")
def full_audit(request: ScanRequest):
    try:
        print(f"Starting audit for {request.repo_url}")
        scan_result = scanner.scan(request.repo_url)
        audit_result = audit_engine.audit(scan_result)
        repo_name = request.repo_url.split("/")[-1].replace(".git", "")
        report_path = report_builder.build(audit_result, repo_name)
        return {
            "status": "success",
            "audit": audit_result,
            "report": report_path
        }
    except Exception as e:
        print("ERROR:", str(e))
        traceback.print_exc()
        raise HTTPException(500, f"Server error: {str(e)}")