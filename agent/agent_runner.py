import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))

def query_llm(prompt):
    print("Querying Gemini Free API...")
    try:
        response = model.generate_content(
            f"You are an expert MLOps agent. Output ONLY valid JSON. No extra text or explanations.\n\n{prompt}"
        )
        text = response.text.strip()
        # Parse JSON
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, indent=2)
        except:
            return text
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    prompt = """
Analyze src/data/sample_dataset.csv (columns: age, income, purchased).
Output ONLY this valid JSON:
{
  "task": "binary_classification",
  "model": "LogisticRegression",
  "features": ["age", "income"],
  "target": "purchased",
  "hyperparams": {"C": 1.0}
}
"""
    plan = query_llm(prompt)
    print("Agent Plan:\n", plan)