import os
from llm_client import chat
from vector_store.retriever import (
    retrieve_courses,
    retrieve_job_role,
    format_courses_for_prompt
)

SYSTEM_PROMPT_BASE = """
You are a career mentor for MSBA students at UT Dallas.

You provide qualitative career guidance based on student interests and goals.
You have access to job role requirements and relevant courses for each query.

Always:
- Explain what the target role involves day to day
- Break down required technical and soft skills clearly
- Recommend specific courses by ID and title that build toward the role
- Be encouraging and honest about what each career path demands
- If a student is undecided, ask about their interests and strengths
"""

def run():
    print("\n💼 CAREER MENTOR")
    print("=" * 50)
    print("Type 'exit' to return to the main menu\n")

    conversation_history = []

    print("Mentor: Hi! I'm here to help you navigate your career path.")
    print("What are your career interests, or do you have a specific role in mind?\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            print("Returning to main menu...\n")
            break

        if not user_input:
            continue

        # Retrieve relevant job role and courses
        job_role = retrieve_job_role(user_input)
        relevant_courses = retrieve_courses(user_input, n_results=8)
        courses_context = format_courses_for_prompt(relevant_courses)

        # Build context string
        job_context = ""
        if job_role:
            job_context = f"""
Closest matching job role:
Title: {job_role['job_title']}
Technical Skills Required: {', '.join(job_role['technical_skills'])}
Soft Skills Required: {', '.join(job_role['soft_skills'])}
"""

        system_prompt = SYSTEM_PROMPT_BASE + f"""
\n{job_context}

Relevant courses for this query:

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

        print(f"\nMentor: {response}\n")

        conversation_history.append({
            "role": "assistant",
            "content": response
        })