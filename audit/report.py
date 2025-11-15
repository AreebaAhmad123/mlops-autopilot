# audit/report.py
from jinja2 import Template
from pathlib import Path

class ReportBuilder:
    def __init__(self, template_dir="audit/templates"):
        self.template_path = Path(template_dir) / "report.md.j2"
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)

    def build(self, audit_result: dict, repo_name: str):
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())

        # ← SIRF TOP 5 FILES DIKHAO
        for check in audit_result["results"]:
            check["files"] = check["files"][:5]  # Limit to 5 files

        md_content = template.render(
            repo_name=repo_name,
            score=audit_result["percentage"],
            total=audit_result["total_score"],
            max_score=audit_result["max_score"],
            checks=audit_result["results"]
        )

        output_file = self.output_dir / f"AUDIT_REPORT_{repo_name}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        return str(output_file)