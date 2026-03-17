from openai import OpenAI
import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # required by the library but not actually validated locally
)

MODEL = "local-model"  # LM Studio ignores this and uses whatever model is loaded

def chat(system_prompt, messages, temperature=0.5):

    combined_messages = [
        {
            "role": "user",
            "content": system_prompt + "\n\n" + messages[0]["content"]
        },
        *messages[1:]
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=combined_messages,
        temperature=temperature,
        max_tokens=512
    )

    return response.choices[0].message.content