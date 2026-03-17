import os
import json
from llm_client import chat
from utils.resume_parser import parse_resume
from utils.semantic_matcher import (
    get_student_skills_from_courses,
    get_job_requirements,
    compute_skills_gap
)
from vector_store.retriever import (
    retrieve_job_role,
    retrieve_courses_for_skills
)

SYSTEM_PROMPT = """
You are a skills gap analyzer for MSBA students at UT Dallas.

You will be given pre-computed skills gap analysis results that have already identified:
- The student's current skills
- Skills they already have that match the target job
- Skills they are missing
- Course recommendations for each missing skill

Your job is to:
- Explain these findings clearly and conversationally to the student
- Highlight the most critical missing technical skills to prioritize
- Make the course recommendations feel actionable and encouraging
- Answer any follow up questions the student has about their gap or recommendations
- Be honest but motivating — gaps are opportunities, not failures

Do not re-compute or second guess the analysis results. 
Trust the pre-computed data and focus on explaining and advising.
"""

def get_student_skills(input_type):
    """
    Returns student skills list based on input type.
    For resume input, returns raw text with a flag.
    """
    if input_type == "1":
        print("\nEnter your completed course IDs separated by commas.")
        print("Example: BUAN 6333, BUAN 6340, BUAN 6312\n")
        raw = input("Completed courses: ").strip()

        if not raw:
            return [], None, "no_courses"

        course_ids = [c.strip() for c in raw.split(",")]
        skills, unrecognized = get_student_skills_from_courses(course_ids)

        if unrecognized:
            print(f"\n⚠ Unrecognized course IDs: {', '.join(unrecognized)}")
            print("These were skipped. Please double check the course IDs.\n")

        return skills, course_ids, "courses"

    elif input_type == "2":
        print("\nEnter the full path to your resume PDF.\n")
        file_path = input("Resume path: ").strip()
        text, error = parse_resume(file_path)

        if error:
            print(f"\n⚠ {error}")
            print("Falling back to manual course input.\n")
            raw = input("Completed courses: ").strip()
            course_ids = [c.strip() for c in raw.split(",")]
            skills, _ = get_student_skills_from_courses(course_ids)
            return skills, course_ids, "courses"

        print("\n✅ Resume parsed successfully.\n")
        return text, None, "resume"

    return [], None, "no_courses"


def build_gap_summary(gap_results, recommendations, job_info, student_skills):
    """
    Builds a structured plain text summary to pass to the LLM.
    The LLM explains this — it does not recompute it.
    """
    matched_lines = "\n".join(
        f"  - {m['required_skill']} (matched with: {m['matched_with']}, "
        f"confidence: {m['score']})"
        for m in gap_results["matched"]
    ) or "  None"

    missing_tech_lines = "\n".join(
        f"  - {s}" for s in gap_results["missing_technical"]
    ) or "  None"

    missing_soft_lines = "\n".join(
        f"  - {s}" for s in gap_results["missing_soft"]
    ) or "  None"

    rec_lines = []
    for skill, courses in recommendations.items():
        course_list = ", ".join(
            f"{c['course_id']} {c['title']}" for c in courses
        )
        rec_lines.append(f"  - {skill}: {course_list}")
    rec_text = "\n".join(rec_lines) or "  No matching courses found"

    summary = f"""
SKILLS GAP ANALYSIS RESULTS
============================
Target Role: {job_info['job_title']}

STUDENT SKILLS IDENTIFIED ({len(student_skills)}):
  {', '.join(student_skills) if student_skills else 'None identified'}

MATCHED SKILLS ({len(gap_results['matched'])}):
{matched_lines}

MISSING TECHNICAL SKILLS ({len(gap_results['missing_technical'])}):
{missing_tech_lines}

MISSING SOFT SKILLS ({len(gap_results['missing_soft'])}):
{missing_soft_lines}

RECOMMENDED COURSES FOR MISSING SKILLS:
{rec_text}
    """.strip()

    return summary


def run():
    print("\n🔍 SKILLS GAP ANALYZER")
    print("=" * 50)
    print("Type 'exit' to return to the main menu\n")

    conversation_history = []

    # Step 1 — input type
    print("How would you like to provide your profile?")
    print("  1. Enter completed courses manually")
    print("  2. Provide resume PDF")
    input_type = input("\nEnter 1 or 2: ").strip()

    # Step 2 — target job
    print()
    target_job = input("What job title are you targeting? ").strip()
    if not target_job:
        target_job = "Data Analyst"
        print(f"No job title provided, defaulting to: {target_job}\n")

    # Step 3 — get student skills
    student_skills, course_ids, flag = get_student_skills(input_type)

    # Step 4 — retrieve job role from vector store
    print("\n⏳ Running semantic skills analysis...\n")
    job_info = retrieve_job_role(target_job)

    if not job_info:
        print("⚠ Could not find a matching job role. Please try a different title.")
        return

    print(f"✅ Matched job role: {job_info['job_title']}\n")

    # Step 5 — compute gap and recommendations
    if flag == "resume":
        # Resume path — pass raw text directly to LLM
        opening_message = (
            f"Here is the student's resume:\n\n{student_skills}\n\n"
            f"Target job title: {job_info['job_title']}\n\n"
            f"Required technical skills: "
            f"{', '.join(job_info['technical_skills'])}\n"
            f"Required soft skills: "
            f"{', '.join(job_info['soft_skills'])}\n\n"
            f"Please perform a skills gap analysis based on the resume "
            f"and job requirements above."
        )

    else:
        # Course path — semantic gap computation first
        gap_results = compute_skills_gap(student_skills, job_info)
        recommendations = retrieve_courses_for_skills(
            gap_results["missing_technical"] + gap_results["missing_soft"],
            n_per_skill=2
        )
        gap_summary = build_gap_summary(
            gap_results, recommendations, job_info, student_skills
        )
        opening_message = (
            f"Here are the pre-computed skills gap results. "
            f"Please explain these to the student clearly:\n\n{gap_summary}"
        )

    # Step 6 — LLM explains the results
    conversation_history.append({
        "role": "user",
        "content": opening_message
    })

    response = chat(
        system_prompt=SYSTEM_PROMPT,
        messages=conversation_history
    )

    print(f"Analyzer: {response}\n")

    conversation_history.append({
        "role": "assistant",
        "content": response
    })

    # Step 7 — follow up conversation loop
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
            system_prompt=SYSTEM_PROMPT,
            messages=conversation_history
        )

        print(f"\nAnalyzer: {response}\n")

        conversation_history.append({
            "role": "assistant",
            "content": response
        })