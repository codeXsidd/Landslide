"""NER-LDI Groq LLM Service. Server-side only. Never expose API key to frontend."""
from typing import Optional

import httpx

from app.config.settings import settings

GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_LLM_MODEL
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def is_available() -> bool:
    return bool(GROQ_API_KEY)


async def chat_completion(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> Optional[str]:
    """Call Groq chat completions API. Returns None if key not configured or on error."""
    if not GROQ_API_KEY:
        return None

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GROQ_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            return None
    except Exception:
        return None


async def explain_risk(risk_state: dict) -> dict:
    """Generate a plain-language explanation of a risk assessment."""
    system = (
        "You are an AI assistant for a landslide early warning system in Northeast India. "
        "Explain risk assessments in clear, actionable language for emergency responders. "
        "Be concise. Focus on what matters for decision-making. "
        "Never claim to be an official warning system."
    )
    user_msg = (
        f"Explain this risk assessment:\n"
        f"Risk Score: {risk_state.get('risk_score', 'N/A')}\n"
        f"Risk Level: {risk_state.get('risk_level', 'N/A')}\n"
        f"Confidence: {risk_state.get('confidence', 'N/A')}\n"
        f"Uncertainty: {risk_state.get('uncertainty_level', 'N/A')}\n"
        f"Major Factors: {risk_state.get('major_factors', [])}\n"
        f"Evidence Status: {risk_state.get('evidence_status', 'N/A')}\n"
        f"Road Blockage Probability: {risk_state.get('road_blockage_probability', 'N/A')}\n"
        f"Village Isolation: {risk_state.get('village_isolation_probability', 'N/A')}\n"
        f"Population Exposed: {risk_state.get('population_exposed', 'N/A')}\n\n"
        "Provide: 1) Plain explanation 2) Key factors 3) Evidence summary 4) Limitations"
    )
    text = await chat_completion(system, user_msg)
    if text is None:
        return {"available": False, "reason": "Groq API not configured or unavailable"}
    return {
        "available": True,
        "explanation": text,
        "model": GROQ_MODEL,
        "disclaimer": "AI-generated explanation. Not an official emergency warning.",
    }


async def emergency_guidance(risk_state: dict, impact: dict, role: str) -> dict:
    """Generate role-specific emergency guidance."""
    system = (
        "You are an AI assistant providing emergency guidance for landslide situations in NE India. "
        f"The user is a {role}. Tailor your response to their role and decision authority. "
        "Be practical and actionable. Reference standard NDMA/SDMA procedures where relevant. "
        "Never issue official warnings - only provide guidance for human decision-makers."
    )
    user_msg = (
        f"Role: {role}\n"
        f"Risk Level: {risk_state.get('risk_level')}, Score: {risk_state.get('risk_score')}\n"
        f"Road Blockage: {impact.get('road_blockage_probability', 0)}\n"
        f"Village Isolation: {impact.get('village_isolation_probability', 0)}\n"
        f"Population at Risk: {impact.get('population_exposed', 0)}\n\n"
        "Provide: 1) Recommended immediate actions 2) Communication steps 3) Monitoring priorities"
    )
    text = await chat_completion(system, user_msg, temperature=0.2)
    if text is None:
        return {"available": False, "reason": "Groq API not configured or unavailable"}
    return {
        "available": True,
        "guidance": text,
        "role": role,
        "model": GROQ_MODEL,
        "disclaimer": "AI-assisted guidance. Human authority required for all actions.",
    }


async def answer_question(question: str, context: str = "") -> dict:
    """Answer a question about landslide risk with optional context."""
    system = (
        "You are an AI assistant for a landslide decision intelligence system. "
        "Answer questions about landslide risk, evidence, and emergency procedures. "
        "If context is provided, base your answer on it. Cite sources when available. "
        "Be concise and accurate. Say 'I don't know' if uncertain."
    )
    user_msg = question
    if context:
        user_msg = f"Context:\n{context}\n\nQuestion: {question}"
    text = await chat_completion(system, user_msg)
    if text is None:
        return {"available": False, "reason": "Groq API not configured or unavailable"}
    return {
        "available": True,
        "answer": text,
        "model": GROQ_MODEL,
        "disclaimer": "AI-generated answer. Verify critical information independently.",
    }
