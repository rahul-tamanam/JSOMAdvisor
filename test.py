from llm_client import chat

response = chat(
    system_prompt="You are a helpful assistant.",
    messages=[{"role": "user", "content": "Say hello in one sentence."}]
)
print(response)