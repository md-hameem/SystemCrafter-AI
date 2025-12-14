from fastapi import APIRouter, status
from orchestrator.core.llm_client import get_llm_client
from orchestrator.core import get_logger

router = APIRouter(prefix="/llm", tags=["LLM"])
logger = get_logger(__name__)


@router.get("/health", status_code=status.HTTP_200_OK)
async def llm_health():
    """Lightweight health check for the configured LLM (Groq).

    Attempts to initialize the Groq client and returns a helpful message
    if initialization fails (for example, due to missing SDK or API key)."""
    try:
        # Attempt to create the client; get_llm_client raises a RuntimeError
        # with a clear message when initialization fails.
        get_llm_client()
        return {"ok": True, "message": "Groq client initialized"}
    except Exception as exc:
        logger.error("LLM health check failed", error=str(exc))
        return {"ok": False, "message": str(exc)}
