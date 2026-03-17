import os
from llm_client import chat
from vector_store.retriever import retrieve_courses, format_courses_for_prompt

SYSTEM_PROMPT_BASE = """
You are an academic advisor for the MSBA (Master of Science in Business 
Analytics and Artificial Intelligence) program at UT Dallas.

Degree rules:
- 36 total credit hours required to graduate
- 18 credit hours must be CORE courses
- 18 credit hours must be ELECTIVE courses (free choice)
- Each course is 3 credit hours
- If a course is listed under 'Only One Of These', the student can only 
  earn credit for ONE course from that group

You will be given a set of relevant courses based on the student's query.
Use these courses to give specific, accurate recommendations.

Always:
- Reference specific course IDs and titles
- Respect prerequisites when sequencing recommendations
- Track completed vs remaining credits when the student provides them
- Clarify the Only One Of These rule when relevant
- Be conversational, encouraging, and concise
"""

def run():
    print("\n📚 DEGREE PLANNER")
    print("=" * 50)
    print("Type 'exit' to return to the main menu\n")

    conversation_history = []
    completed_courses = []

    # Opening
    print("Advisor: Hi! I'm your MSBA degree planning advisor.")
    print("Are you a new student or have you completed some courses already?\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Returning to main menu...\n")
            break

        if not user_input:
            continue

        # Retrieve relevant courses based on the student's query
        relevant_courses = retrieve_courses(user_input, n_results=10)
        courses_context = format_courses_for_prompt(relevant_courses)

        # Build dynamic system prompt with only relevant courses
        system_prompt = SYSTEM_PROMPT_BASE + f"""
\nHere are the most relevant courses for this query:

{courses_context}
"""

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