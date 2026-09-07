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
{text[:8000]}

Identify ALL genuinely risky clauses. Be thorough. If the contract has less than 10 risky clauses, flag all of them. If the contract is largely fair, flag only what is truly problematic. Use your best legal judgment — do not invent issues that are not there.
Return ONLY valid JSON, no explanation, no backticks, no markdown.
(Important - You MUST end your response with a complete valid JSON object. No text after the JSON.)
Like below:
{{
    "contract_type": "type of contract (e.g. Employment Agreement, NDA, Lease Agreement)",
    "overall_risk": "Low or Medium or High",
    "risk_score": <number 0-100>,
    "summary": "2-3 sentence summary of the contract and overall risk for the {role}",
    "flagged_clauses": [
        {{
            "clause": "copy the exact original clause text from the contract verbatim — never leave this empty",
            "risk_level": "Low or Medium or High — never leave this empty",
            "reason": "specific explanation of why this clause is risky or unfavorable for the {role} — never leave this empty",
            "suggestion": "Rewrite this clause verbatim as it would appear in the actual contract, in formal legal language, that is fair and balanced for all parties while better protecting the {role}'s reasonable interests. Write it as a complete contract clause, not as advice or commentary — never leave this empty"
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