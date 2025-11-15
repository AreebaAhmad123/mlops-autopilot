import os
import json
import tempfile
import shutil
import logging
from pathlib import Path
from git import Repo
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RepoScanner:
    def __init__(self, temp_dir: str = None):
        self.temp_dir = temp_dir or tempfile.mkdtemp(prefix="mlops_audit_")
        logger.info(f"Using temp dir: {self.temp_dir}")

    def clone_repo(self, repo_url: str, branch: str = "main") -> Path:
        clone_path = Path(self.temp_dir) / "cloned_repo"
        try:
            Repo.clone_from(repo_url, clone_path, branch=branch)
            logger.info(f"Cloned {repo_url} ({branch})")
            return clone_path
        except Exception as e:
            # try fallback to master if main fails
            if "main" in branch.lower():
                logger.warning("main not found – trying master")
                return self.clone_repo(repo_url, branch="master")
            logger.error(f"Clone failed: {e}")
            raise ValueError(f"Failed to clone {repo_url}: {e}")

    def scan_structure(self, repo_path: Path) -> Dict[str, Any]:
        structure = {
            "files": [], "directories": [], "ml_patterns": {
                "python_scripts": [], "config_files": [], "docker_files": [],
                "test_files": [], "data_folders": [], "model_files": []
            },
            "total_files": 0, "total_dirs": 0
        }
        for root, dirs, files in os.walk(repo_path):
            rel_root = os.path.relpath(root, repo_path)
            if rel_root != ".":
                structure["directories"].append(rel_root)
                structure["total_dirs"] += 1
            for f in files:
                fp = Path(root) / f
                rel = fp.relative_to(repo_path)
                structure["files"].append(str(rel))
                structure["total_files"] += 1
                low = f.lower()
                if low.endswith('.py'):
                    structure["ml_patterns"]["python_scripts"].append(str(rel))
                elif f in ('Dockerfile', 'docker-compose.yml'):
                    structure["ml_patterns"]["docker_files"].append(str(rel))
                elif low.endswith(('.yaml', '.yml')):
                    structure["ml_patterns"]["config_files"].append(str(rel))
                elif 'test' in rel_root.lower() or f.startswith('test_'):
                    structure["ml_patterns"]["test_files"].append(str(rel))
                elif any(ext in low for ext in ['.csv','.json','.data']):
                    if 'data' in rel_root.lower():
                        structure["ml_patterns"]["data_folders"].append(rel_root)
                elif any(ext in low for ext in ['.pkl','.h5','.joblib','.pth']):
                    structure["ml_patterns"]["model_files"].append(str(rel))
        return structure

    def generate_report(self, repo_url: str, structure: Dict) -> str:
        report = {
            "repo_url": repo_url,
            "scan_timestamp": str(Path().resolve().stat().st_mtime),
            "structure": structure
        }
        out_path = Path(self.temp_dir) / "scan_report.json"
        with open(out_path, 'w') as f:
            json.dump(report, f, indent=2)
        return str(out_path)

    def cleanup(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("Temp dir removed")

def main(repo_url: str, branch: str = "main", out_dir: str = "outputs"):
    scanner = RepoScanner()
    try:
        repo_path = scanner.clone_repo(repo_url, branch)
        struct = scanner.scan_structure(repo_path)
        rpt = scanner.generate_report(repo_url, struct)
        Path(out_dir).mkdir(exist_ok=True)
        shutil.copy(rpt, Path(out_dir) / "scan_report.json")
        print(f"Scan report → {out_dir}/scan_report.json")
    finally:
        scanner.cleanup()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python src/scanner/repo_scanner.py <repo_url> [branch]")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else "main")