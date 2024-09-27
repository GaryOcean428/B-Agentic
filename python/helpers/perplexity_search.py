import openai
from typing import Any, Dict, List, Optional

def get_api_key(service_name: str) -> str:
    # Function to retrieve API key for the specified service
    # Replace this with your method of fetching API keys
    api_keys = {
        'perplexity': 'YOUR_PERPLEXITY_API_KEY'
    }
    return api_keys.get(service_name, '')

def perplexity_search(
    query: str,
    model_name: str = "llama-3.1-sonar-large-128k-online",
    api_key: Optional[str] = None,
    base_url: str = "https://api.perplexity.ai",
) -> str:
    api_key = api_key or get_api_key("perplexity")

    openai.api_key = api_key
    openai.api_base = base_url  # type: ignore  # Suppress type checker error

    messages = [
        {
            "role": "user",
            "content": query,
        },
    ]

    response = openai.ChatCompletion.create(  # type: ignore
        model=model_name,
        messages=messages,
    )
    result = response['choices'][0]['message']['content']
    return result
