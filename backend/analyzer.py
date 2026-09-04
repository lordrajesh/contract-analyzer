from ollama import Client
from config import OLLAMA_HOST, OLLAMA_MODEL
import json

client = Client(host=OLLAMA_HOST)


def analyze_contract(text: str, role: str) -> dict:
    prompt = f"""You are an expert contract lawyer analyzing a contract.

The user is the: {role}

Analyze the following contract strictly from the {role}'s perspective and identify clauses that are risky, unfavorable, or unusual for them.

Contract text:
{text[:6000]}

Return ONLY valid JSON, no explanation, no backticks:
{{
    "contract_type": "type of contract (e.g. Employment Agreement, NDA, Lease Agreement)",
    "overall_risk": "Low or Medium or High",
    "risk_score": <number 0-100>,
    "summary": "2-3 sentence summary of the contract and overall risk for the {role}",
    "flagged_clauses": [
        {{
            "clause": "exact or paraphrased text of the risky clause",
            "risk_level": "Low or Medium or High",
            "reason": "why this is risky for the {role}",
            "suggestion": "improved version of this clause that better protects the {role}"
        }}
    ]
}}"""

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.message.content.strip()
    print(f"Raw LLM response:\n{content[:500]}")

    # Strip thinking tags
    if "<think>" in content and "</think>" in content:
        content = content.split("</think>")[-1].strip()

    # Extract JSON from response
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0].strip()
    elif "```" in content:
        content = content.split("```")[1].split("```")[0].strip()

    # Find JSON object
    start = content.find("{")
    end = content.rfind("}") + 1
    if start != -1 and end > start:
        content = content[start:end]

    print(f"Cleaned content:\n{content[:500]}")

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        return {"error": f"LLM returned invalid JSON: {content[:200]}"}