from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # required by the library but not actually validated locally
)

MODEL = "local-model"  # LM Studio ignores this and uses whatever model is loaded

def chat(system_prompt, messages, temperature=0.5):
    """
    system_prompt: str
    messages: list of {"role": "user"/"assistant", "content": "..."}
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            *messages
        ],
        temperature=temperature,
        max_tokens=512
    )
    return response.choices[0].message.content