"""
NER-SAGE — RAG Generation Pipeline
Uses the Groq API (Llama 3.3) to generate actionable insights based on retrieved SOPs.
"""

import structlog
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

from app.config.settings import settings
from app.rag.retrieval import retrieve_context

logger = structlog.get_logger(__name__)

PROMPT_TEMPLATE = """
You are NER-SAGE, an AI decision-support system for disaster management in Northeast India.
A critical situation has been detected. You need to provide a recommended action plan based ONLY on the provided standard operating procedures (SOPs).

CRITICAL SITUATION:
{situation_description}

RELEVANT SOPs / CONTEXT:
{context}

Based on the SOPs above, what are the immediate recommended actions?
If the SOPs do not cover this specific scenario, state that clearly and provide general best practices.
Format your response as a concise, bulleted list.
"""

def generate_action_plan(situation_description: str) -> str:
    """
    Full RAG pipeline: Retrieves context from Qdrant and generates a response using Groq.
    """
    if not settings.GROQ_API_KEY or "YOUR_GROQ_API_KEY_HERE" in settings.GROQ_API_KEY:
        return "Error: GROQ_API_KEY is missing or invalid. Cannot generate action plan."

    # 1. Retrieve Context
    logger.info("Retrieving context from Qdrant...")
    context = retrieve_context(situation_description, top_k=3)

    # 2. Setup LLM
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_LLM_MODEL,
        temperature=0.2, # Low temperature for more deterministic/factual output
    )

    # 3. Generate
    prompt = PromptTemplate(
        input_variables=["situation_description", "context"],
        template=PROMPT_TEMPLATE
    )

    chain = prompt | llm

    logger.info("Generating response via Groq API...")
    try:
        response = chain.invoke({
            "situation_description": situation_description,
            "context": context
        })
        return response.content
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return f"Error connecting to LLM: {str(e)}"
