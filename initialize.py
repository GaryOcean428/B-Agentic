from agent_config import AgentConfig
import openai
from typing import Any, Dict, List
from python.helpers import files


def get_openai_chat(model_name: str = "gpt-3.5-turbo", temperature: float = 0.0):
    # Function to create a chat completion function
    def chat_completion(messages: List[Dict[str, Any]]) -> str:
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            temperature=temperature
        )
        return response['choices'][0]['message']['content']
    return chat_completion


def get_openai_embedding(model: str = "text-embedding-ada-002"):
    # Function to create an embedding function
    def embedding_function(input_text: str) -> List[float]:
        response = openai.Embedding.create(  # type: ignore
            model=model,
            input=input_text
        )
        return response['data'][0]['embedding']
    return embedding_function

# Add a blank line before the function
def initialize():
    # Main chat model used by agents
    chat_llm = get_openai_chat(model_name="gpt-3.5-turbo", temperature=0)

    # Utility model used for helper functions
    utility_llm = chat_llm

    # Embedding model used for memory
    embedding_llm = get_openai_embedding(model="text-embedding-ada-002")

    # Agent configuration
    config = AgentConfig(
        chat_model=chat_llm,
        utility_model=utility_llm,
        embeddings_model=embedding_llm,
        auto_memory_count=0,
        rate_limit_requests=15,
        max_tool_response_length=3000,
        code_exec_docker_enabled=True,
        code_exec_docker_volumes={
            files.get_abs_path("work_dir"): {"bind": "/root", "mode": "rw"}
        },
        code_exec_ssh_enabled=True,
    )

    return config
