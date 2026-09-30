import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from deepeval.models import DeepEvalBaseLLM
from openai import OpenAI

# Load src/.env if it exists, otherwise fallback to default .env
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
load_dotenv()

# Judge model — intentionally different from the generation model to avoid self-evaluation bias.
# Uses OpenRouter with the same API key, but routed to Gemma 3 27B.
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "openai/gpt-oss-120b")
JUDGE_THRESHOLD_SUMMARY = float(os.getenv("JUDGE_THRESHOLD_SUMMARY", "0.5"))
JUDGE_THRESHOLD_HALLUCINATION = float(os.getenv("JUDGE_THRESHOLD_HALLUCINATION", "0.5"))
JUDGE_THRESHOLD_FAITHFULNESS = float(os.getenv("JUDGE_THRESHOLD_FAITHFULNESS", "0.5"))
JUDGE_THRESHOLD_RELEVANCY = float(os.getenv("JUDGE_THRESHOLD_RELEVANCY", "0.5"))
JUDGE_THRESHOLD_PRECISION = float(os.getenv("JUDGE_THRESHOLD_PRECISION", "0.5"))


class OpenRouterJudge(DeepEvalBaseLLM):
    """Wraps OpenRouter as a DeepEval-compatible LLM judge."""

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.getenv("JUDGE_MODEL", JUDGE_MODEL)
        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )

    def load_model(self):
        return self.client

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=8192,
        )
        msg = response.choices[0].message
        content = msg.content
        if not content and hasattr(msg, "reasoning") and msg.reasoning:
            content = msg.reasoning
        return content or ""

    async def a_generate(self, prompt: str) -> str:
        # DeepEval calls this from its own event loop (inside run_in_executor thread).
        # We offload the blocking HTTP call to a sub-thread so DeepEval's asyncio.gather
        # can run all metrics truly in parallel without blocking its event loop.
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.generate, prompt)

    def get_model_name(self) -> str:
        return self.model_name


def get_judge_llm() -> OpenRouterJudge:
    return OpenRouterJudge()
