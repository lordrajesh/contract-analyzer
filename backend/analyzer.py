from ollama import Client
from config import OLLAMA_HOST, OLLAMA_MODEL
import json

client = Client(host=OLLAMA_HOST)


def extract_outermost_json(text: str) -> str:
    """
    Find the JSON block that contains 'contract_type' — 
    our expected top-level field. Searches from end backwards
    since qwen3 puts final answer last in thinking mode.
    """
    pos = len(text)
    while True:
        end = text.rfind("}", 0, pos)
        if end == -1:
            break
        depth = 0
        start = -1
        for i in range(end, -1, -1):
            if text[i] == "}":
                depth += 1
            elif text[i] == "{":
                depth -= 1
                if depth == 0:
                    start = i
                    break
        if start != -1:
            candidate = text[start:end+1]
            try:
                parsed = json.loads(candidate)
                if "contract_type" in parsed:
                    return candidate
            except:
                pass
        pos = end
    return None


def analyze_contract(text: str, role: str) -> dict:
    prompt = f"""You are an expert contract lawyer analyzing a contract.

The user is the: {role}

Analyze the following contract strictly from the {role}'s perspective and identify clauses that are risky, unfavorable, or unusual for them.

Contract text:
{text}

Return ONLY valid JSON, no explanation, no backticks, no markdown:
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

    print(f"Content length: {len(response.message.content)}")
    print(f"Thinking length: {len(response.message.thinking) if hasattr(response.message, 'thinking') and response.message.thinking else 0}")

    # Use thinking field if content empty
    content = response.message.content.strip()
    if not content and hasattr(response.message, 'thinking') and response.message.thinking:
        print("Using thinking field")
        content = response.message.thinking.strip()

    # Extract correct JSON block
    extracted = extract_outermost_json(content)

    if extracted:
        print(f"Found JSON: {extracted[:200]}")
        try:
            return json.loads(extracted)
        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            return {"error": f"Parse failed: {str(e)}"}

    print("No valid JSON found")
    return {"error": "Could not find valid JSON in response"}