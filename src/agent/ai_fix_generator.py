# src/agent/ai_fix_generator.py
import os
import json
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()  # reads .env in project root
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

class AIFixGenerator:
    def __init__(self, audit_path: str):
        with open(audit_path, "r", encoding="utf-8") as f:
            self.audit = json.load(f)
        logger.info("Loaded audit report")
        self.struct = self.audit.get("structure", {})
        self.env = Environment(loader=FileSystemLoader("agent/prompts"))

    def _gemini(self, prompt: str) -> str:
        model = genai.GenerativeModel(MODEL)
        resp = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        return resp.text.strip()

    def generate(self, component: str) -> str:
        tmpl = self.env.get_template("fix_prompt.j2")
        prompt = tmpl.render(
            audit_results=self.audit,
            structure=self.struct,
            component=component
        )
        return self._gemini(prompt)

    def run_all(self, out_dir: str = "fixes"):
        missing = self.audit.get("missing_components", [])
        out_path = Path(out_dir)
        out_path.mkdir(exist_ok=True)
        generated = []

        for comp in missing:
            if comp == "docker":
                content = self.generate("Dockerfile")
                p = out_path / "Dockerfile"
            elif comp == "mlflow":
                content = self.generate("mlflow.yaml")
                p = out_path / "mlflow.yaml"
            elif comp == "tests":
                content = self.generate("pytest unit tests")
                p = out_path / "tests" / "test_example.py"
                p.parent.mkdir(exist_ok=True)
            else:
                continue

            p.write_text(content, encoding="utf-8")
            generated.append(str(p))
            logger.info(f"Wrote {p}")

        return generated

def main(audit_path: str):
    gen = AIFixGenerator(audit_path)
    files = gen.run_all()
    print("Fixes → ./fixes")
    for f in files:
        print("  •", f)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python src/agent/ai_fix_generator.py <audit_report.json>")
        sys.exit(1)
    main(sys.argv[1])