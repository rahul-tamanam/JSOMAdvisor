import os
from llm_client import chat
from data_loader import get_courses_context, get_skills_context
from utils.resume_parser import parse_resume

def load_prompt():
    prompt_path = os.path.join(
        os.path.dirname(__file__), "..", "prompts", "skills_gap.txt"
    )
    with open(prompt_path) as f:
        template = f.read()
    return (template
            .replace("{skills}", get_skills_context())
            .replace("{courses}", get_courses_context()))

def get_student_profile():
    """
    Asks the student whether they want to input courses manually
    or provide a resume path. Returns a profile string to inject
    into the conversation.
    """
    print("\nHow would you like to provide your profile?")
    print("  1. Enter completed courses manually")
    print("  2. Provide resume PDF path")
    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "1":
        print("\nEnter your completed course IDs separated by commas.")
        print("Example: BUAN 6333, BUAN 6340, BUAN 6312\n")
        courses_input = input("Completed courses: ").strip()
        if not courses_input:
            return "The student has not completed any courses yet."
        return f"The student has completed the following courses: {courses_input}"

    elif choice == "2":
        print("\nEnter the full path to your resume PDF.")
        print("Example: C:/Users/yourname/Documents/resume.pdf\n")
        file_path = input("Resume path: ").strip()

        text, error = parse_resume(file_path)
        if error:
            print(f"\n⚠ {error}")
            print("Falling back to manual course input.\n")
            courses_input = input("Completed courses: ").strip()
            return f"The student has completed the following courses: {courses_input}"

        print("\n✅ Resume parsed successfully.\n")
        return f"The student has provided the following resume:\n\n{text}"

    else:
        print("Invalid choice, defaulting to manual input.")
        courses_input = input("Completed courses: ").strip()
        return f"The student has completed the following courses: {courses_input}"


def run():
    print("\n🔍 SKILLS GAP ANALYZER")
    print("=" * 50)
    print("Type 'exit' to return to the main menu\n")

    system_prompt = load_prompt()
    conversation_history = []

    # Get student profile upfront before chat begins
    profile = get_student_profile()

    # Ask for target job title
    print()
    target_job = input("What job title are you targeting? ").strip()
    if not target_job:
        target_job = "not specified yet"

    # Build the opening message with profile and target job injected
    opening_message = (
        f"{profile}\n\n"
        f"My target job title is: {target_job}\n\n"
        f"Please perform a skills gap analysis for me."
    )

    conversation_history.append({
        "role": "user",
        "content": opening_message
    })

    # Get initial analysis
    print("\nAnalyzing your profile...\n")
    response = chat(
        system_prompt=system_prompt,
        messages=conversation_history
    )

    print(f"Analyzer: {response}\n")

    conversation_history.append({
        "role": "assistant",
        "content": response
    })

    # Continue conversation for follow up questions
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

        print(f"\nAnalyzer: {response}\n")

        conversation_history.append({
            "role": "assistant",
            "content": response
        })