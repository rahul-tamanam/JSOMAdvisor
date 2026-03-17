from sentence_transformers import SentenceTransformer, util
import json
import os
import torch
import os
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
MATCH_THRESHOLD = 0.60

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

def load_courses():
    with open(os.path.join(DATA_DIR, "courses.json")) as f:
        return json.load(f)

def load_skills():
    # Update this filename to match what you have in /data
    for name in ["skills_clean.json", "skills.json"]:
        path = os.path.join(DATA_DIR, name)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    raise FileNotFoundError("No skills JSON file found in data/")


def get_student_skills_from_courses(completed_course_ids):
    courses = load_courses()
    course_map = {c["course_id"].strip().upper(): c for c in courses}

    student_skills = set()
    unrecognized = []

    for course_id in completed_course_ids:
        normalized = course_id.strip().upper()
        if normalized in course_map:
            skills = course_map[normalized].get("skills_taught") or []
            for skill in skills:
                if skill:
                    student_skills.add(skill.strip())
        else:
            unrecognized.append(course_id)

    return list(student_skills), unrecognized


def get_job_requirements(job_title):
    skills_data = load_skills()
    job_titles = [s["job_title"] for s in skills_data]

    query_embedding = MODEL.encode(job_title, convert_to_tensor=True)
    title_embeddings = MODEL.encode(job_titles, convert_to_tensor=True)

    similarities = util.cos_sim(query_embedding, title_embeddings)[0]
    best_idx = int(torch.argmax(similarities))
    best_score = float(similarities[best_idx])

    matched_job = skills_data[best_idx]

    return {
        "job_title":        matched_job["job_title"],
        "confidence":       round(best_score, 2),
        "technical_skills": matched_job["technical_skills"],
        "soft_skills":      matched_job["soft_skills"]
    }


def compute_skills_gap(student_skills, job_requirements):
    technical_required = job_requirements["technical_skills"]
    soft_required      = job_requirements["soft_skills"]
    all_required       = technical_required + soft_required

    if not student_skills or not all_required:
        return {
            "matched":            [],
            "missing_technical":  technical_required,
            "missing_soft":       soft_required
        }

    student_embeddings  = MODEL.encode(student_skills,  convert_to_tensor=True)
    required_embeddings = MODEL.encode(all_required,    convert_to_tensor=True)

    similarity_matrix = util.cos_sim(required_embeddings, student_embeddings)

    matched           = []
    missing_technical = []
    missing_soft      = []

    for i, required_skill in enumerate(all_required):
        best_score         = float(similarity_matrix[i].max())
        best_student_skill = student_skills[int(similarity_matrix[i].argmax())]
        is_technical       = required_skill in technical_required

        if best_score >= MATCH_THRESHOLD:
            matched.append({
                "required_skill": required_skill,
                "matched_with":   best_student_skill,
                "score":          round(best_score, 2),
                "type":           "technical" if is_technical else "soft"
            })
        else:
            if is_technical:
                missing_technical.append(required_skill)
            else:
                missing_soft.append(required_skill)

    return {
        "matched":           matched,
        "missing_technical": missing_technical,
        "missing_soft":      missing_soft
    }