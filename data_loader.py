import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_courses():
    with open(os.path.join(DATA_DIR, "courses.json")) as f:
        return json.load(f)

def load_skills():
    with open(os.path.join(DATA_DIR, "skills.json")) as f:
        return json.load(f)

def get_courses_context():
    courses = load_courses()
    # Only inject fields the bot actually needs, keeps context small
    slim = []
    for c in courses:
        slim.append({
            "course_id": c["course_id"],
            "title": c["title"],
            "credits": c["credits"],
            "course_type": c["course_type"],
            "prerequisites": c.get("prerequisites"),
            "skills_taught": c.get("skills_taught", [])
        })
    return json.dumps(slim, indent=2)

def get_skills_context():
    skills = load_skills()
    return json.dumps(skills, indent=2)