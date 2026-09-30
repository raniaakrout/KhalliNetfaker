
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from openai import RateLimitError

load_dotenv()

# Create and configure a chat model
def create_model(model_name: str):
    return init_chat_model(
        model=model_name,
        model_provider="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=float(os.getenv("TEMPERATURE", 0)),
        max_retries=int(os.getenv("MAX_RETRIES", 2)),
        max_tokens=int(os.getenv("MAX_TOKENS", 2048)),  # Limite explicite pour éviter les 402
    )




def get_llm():
    model = create_model(os.getenv("PRIMARY_MODEL", "gpt-oss-120b"))

    print(f"Using model: {os.getenv('PRIMARY_MODEL')}")
    print(f"DEBUG: model class is {model.__class__.__name__}")
    print(f"DEBUG: model max_tokens is {getattr(model, 'max_tokens', 'N/A')}")
    print(f"DEBUG: model kwargs are {getattr(model, 'model_kwargs', 'N/A')}")

    return model