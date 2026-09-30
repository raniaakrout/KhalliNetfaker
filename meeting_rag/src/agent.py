import json
import uuid

from langchain_core.messages import AIMessage
from langchain.agents.middleware.types import wrap_model_call
from langchain.agents import create_agent

from llm_utils import get_llm
from memory import get_memory
from rag.tools import make_chat_tools
from prompts.rag_prompt import RAG_SYSTEM_PROMPT


# =========================================================
# Middleware to parse JSON tool calls
# =========================================================

@wrap_model_call
def json_tool_parser(request, handler):
    response = handler(request)
    
    try:
        # Check if the result has a message
        if hasattr(response, "result") and response.result:
            msg = response.result[-1]
            if isinstance(msg, AIMessage) and not msg.tool_calls:
                text = msg.content.strip()
                if text.startswith("```json"):
                    text = text[7:-3].strip()
                elif text.startswith("```"):
                    text = text[3:-3].strip()
                
                parsed = json.loads(text)
                if isinstance(parsed, dict) and "name" in parsed:
                    msg.tool_calls = [{
                        "name": parsed["name"],
                        "args": parsed.get("parameters", {}),
                        "id": f"call_{uuid.uuid4().hex[:8]}"
                    }]
                    # Clear the content since we converted it to a tool call
                    msg.content = ""
    except Exception:
        pass
        
    return response


# =========================================================
# Chat agent — ReAct: search | summarize | direct reply
# =========================================================

def create_chat_agent(transcript_id: str | None):
    """
    One agent per transcript. Tools are bound via make_chat_tools(transcript_id).
    The LLM decides: search_meeting, get_meeting_summary, or no tool.
    Conversation memory is persisted in PostgreSQL via the LangGraph checkpointer.
    """
    return create_agent(
        model=get_llm(),
        tools=make_chat_tools(transcript_id),
        system_prompt=RAG_SYSTEM_PROMPT,
        checkpointer=get_memory(),
        middleware=[json_tool_parser],
    )


# Backward-compatible alias
create_rag_agent = create_chat_agent
