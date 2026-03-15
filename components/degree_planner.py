import os
from llm_client import chat
from data_loader import get_courses_context

def load_prompt():
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "degree_planner.txt"
    )
    with open(prompt_path) as f:
        template = f.read()
    return template.replace("{courses}", get_courses_context())

def run():
    print("\n📚 DEGREE PLANNER")
    print("=" * 50)
    print("Type 'exit' to return to the main menu\n")

    system_prompt = load_prompt()
    conversation_history = []

    # Opening message from the bot
    opening = chat(
        system_prompt=system_prompt,
        messages=[{
            "role": "user",
            "content": "Hello, I need help planning my degree."
        }]
    )
    print(f"Advisor: {opening}\n")
    conversation_history.append({
        "role": "user",
        "content": "Hello, I need help planning my degree."
    })
    conversation_history.append({
        "role": "assistant",
        "content": opening
    })

    # Conversation loop
    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Returning to main menu...\n")
            break

        if not user_input:
            continue

        conversation_history.append({
            "role": "user",
            "content": user_input
        })

        response = chat(
            system_prompt=system_prompt,
            messages=conversation_history
        )

        print(f"\nAdvisor: {response}\n")

        conversation_history.append({
            "role": "assistant",
            "content": response
        })