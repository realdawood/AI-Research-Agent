from langchain_ollama import ChatOllama
from langchain_core.tools import tool


@tool
def calculator(number: int) -> int:
    """Return double of a number."""
    return number * 2


llm = ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)

llm_with_tools = llm.bind_tools([calculator])

response = llm_with_tools.invoke(
    "Double the number 10 using the calculator tool."
)

print(response)