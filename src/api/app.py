from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import logging
from typing import Optional
from src.scanner.repo_scanner import RepoScanner  # Adjust path if needed

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MLOps Autopilot Auditor API",
    description="API for auditing ML repos",
    version="0.1.0"
)

class ScanRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = "main"

class ScanResponse(BaseModel):
    report_path: str
    structure_summary: dict

@app.get("/health")
async def health_check():
    """Simple health endpoint for monitoring."""
    return {"status": "healthy"}

@app.post("/scan", response_model=ScanResponse)
async def scan_repo(request: ScanRequest):
    """
    Endpoint to scan a repo.
    :param request: JSON with repo_url and optional branch
    :return: JSON with report path and structure summary
    """
    try:
        scanner = RepoScanner()
        repo_path = scanner.clone_repo(request.repo_url, request.branch)
        structure = scanner.scan_structure(repo_path)
        report_path = scanner.generate_report(request.repo_url, structure)
        
        # For API, we return summary; full report in outputs/
        summary = structure["ml_patterns"]  # Or full structure if needed
        
        return {"report_path": report_path, "structure_summary": summary}
    
    except ValueError as e:
        logger.error(f"Scan error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        scanner.cleanup()

# Run with: uvicorn src.api.app:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)