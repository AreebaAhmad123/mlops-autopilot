# audit/engine.py
from typing import Dict

class MLOpsAuditEngine:
    def __init__(self):
        self.checks = {
            "data": {"weight": 10, "name": "Data Pipeline"},
            "training": {"weight": 10, "name": "Training Script"},
            "inference": {"weight": 10, "name": "Inference Code"},
            "requirements": {"weight": 10, "name": "Dependencies"},
            "docker": {"weight": 15, "name": "Containerization"},
            "mlflow": {"weight": 15, "name": "Experiment Tracking"},
            "tests": {"weight": 10, "name": "Unit Tests"},
            "ci_cd": {"weight": 15, "name": "CI/CD"},
            "monitoring": {"weight": 5, "name": "Monitoring"},
            "config": {"weight": 5, "name": "Config Management"}
        }

    def audit(self, scan_data: Dict) -> Dict:
        detected = scan_data.get("detected", {})  # ← SAFE
        files_data = scan_data.get("files", {})   # ← SAFE
        
        total_score = 0
        max_score = sum(c["weight"] for c in self.checks.values())
        results = []

        # ← YE SAB ANDAR HONA CHAHIYE
        for key, check in self.checks.items():
            passed = detected.get(key, False)  # ← SAFE
            score = check["weight"] if passed else 0
            total_score += score
            results.append({
                "check": check["name"],
                "passed": passed,
                "score": score,
                "weight": check["weight"],
                "files": files_data.get(key, [])  # ← SAFE
            })

        percentage = (total_score / max_score) * 100 if max_score > 0 else 0

        return {
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "results": results,
            "repo_path": scan_data.get("repo_path", "unknown")
        }