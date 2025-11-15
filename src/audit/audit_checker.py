# src/audit/audit_checker.py
import json, logging
from pathlib import Path
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuditChecker:
    def __init__(self, scan_path: str):
        self.scan = self._load(scan_path)

    def _load(self, p):
        with open(p) as f: data = json.load(f)
        logger.info("Loaded scan")
        return data

    def run(self) -> Dict:
        checks = [self._structure, self._ci_cd, self._mlflow,
                  self._tests, self._docker, self._versioning, self._repro]
        res = {"scores":{}, "missing_components":[], "details":{}}
        total = 0
        for fn in checks:
            cat, sc, det = fn()
            res["scores"][cat] = sc
            res["details"][cat] = det
            if sc < 100: res["missing_components"].append(cat)
            total += sc
        res["overall_score"] = total // len(checks)
        self._save(res)
        return res

    def _save(self, data):
        p = Path("outputs") / "audit_report.json"
        p.parent.mkdir(exist_ok=True)
        with open(p, "w") as f: json.dump(data, f, indent=2)
        logger.info(f"Audit → {p}")

    def _structure(self) -> Tuple[str,int,Dict]:
        s = self.scan["structure"]["ml_patterns"]
        issues, sc = [], 100
        if not s["data_folders"]: issues.append("no data folder"); sc-=30
        if not s["model_files"]: issues.append("no model artifacts"); sc-=30
        if not any("src" in d for d in self.scan["structure"]["directories"]):
            issues.append("no src/"); sc-=40
        return "structure", max(sc,0), {"issues":issues}

    def _ci_cd(self) -> Tuple[str,int,Dict]:
        has = any(".github/workflows" in d for d in self.scan["structure"]["directories"])
        return "ci_cd", 100 if has else 0, {"has":has}

    def _mlflow(self) -> Tuple[str,int,Dict]:
        files = self.scan["structure"]["files"]
        yaml_ok = any("mlflow.yaml" in f for f in files)
        code_ok = any("mlflow" in f for f in self.scan["structure"]["ml_patterns"]["python_scripts"])
        sc = 100 if yaml_ok else (50 if code_ok else 0)
        return "mlflow", sc, {"yaml":yaml_ok, "code":code_ok}

    def _tests(self) -> Tuple[str,int,Dict]:
        has = bool(self.scan["structure"]["ml_patterns"]["test_files"])
        return "tests", 100 if has else 0, {"has":has}

    def _docker(self) -> Tuple[str,int,Dict]:
        has = bool(self.scan["structure"]["ml_patterns"]["docker_files"])
        return "docker", 100 if has else 0, {"has":has}

    def _versioning(self) -> Tuple[str,int,Dict]:
        has = any(f in self.scan["structure"]["files"] for f in [".dvc","dvc.yaml"])
        return "versioning", 100 if has else 0, {"has":has}

    def _repro(self) -> Tuple[str,int,Dict]:
        has = any("requirements.txt" in f for f in self.scan["structure"]["files"])
        return "reproducibility", 100 if has else 0, {"has_req":has}

def main(scan_path):
    a = AuditChecker(scan_path)
    a.run()
    print("Audit finished → outputs/audit_report.json")

if __name__ == "__main__":
    import sys
    if len(sys.argv)<2:
        print("Usage: python src/audit/audit_checker.py <scan_report.json>")
        sys.exit(1)
    main(sys.argv[1])