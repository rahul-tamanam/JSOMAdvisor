import json
import os
import chromadb
from chromadb.utils import embedding_functions

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

def get_client():
    return chromadb.PersistentClient(path=DB_DIR)

def retrieve_courses(query, n_results=8, course_type_filter=None):
    client = get_client()
    collection = client.get_collection("courses", embedding_function=ef)

    where = None
    if course_type_filter:
        where = {"course_type": course_type_filter}

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where=where
    )

    courses = []
    for metadata in results["metadatas"][0]:
        courses.append({
            "course_id":         metadata.get("course_id", ""),
            "title":             metadata.get("title", ""),
            "credits":           float(metadata.get("credits", 3)),
            "course_type":       metadata.get("course_type", ""),
            "description":       metadata.get("description", ""),
            "prerequisites":     json.loads(metadata.get("prerequisites", "[]")),
            "only_one_of_these": json.loads(metadata.get("only_one_of_these", "[]")),
            "skills_taught":     json.loads(metadata.get("skills_taught", "[]"))
        })

    return courses

def retrieve_job_role(job_title):
    """
    Finds the closest matching job role for a given title.
    Returns the job role dict with technical and soft skills.
    """
    client = get_client()
    collection = client.get_collection("skills", embedding_function=ef)

    results = collection.query(
        query_texts=[job_title],
        n_results=1
    )

    if not results["metadatas"][0]:
        return None

    metadata = results["metadatas"][0][0]
    return {
        "job_title":        metadata["job_title"],
        "technical_skills": json.loads(metadata["technical_skills"]),
        "soft_skills":      json.loads(metadata["soft_skills"])
    }


def retrieve_courses_for_skills(skills_list, n_per_skill=2):
    """
    For a list of skills, retrieves relevant courses for each.
    Used by the skills gap analyzer to recommend courses.
    Returns a dict of skill -> list of courses
    """
    client = get_client()
    collection = client.get_collection("courses", embedding_function=ef)

    recommendations = {}

    for skill in skills_list:
        results = collection.query(
            query_texts=[skill],
            n_results=n_per_skill
        )

        courses = []
        seen = set()
        for metadata in results["metadatas"][0]:
            cid = metadata["course_id"]
            if cid not in seen:
                seen.add(cid)
                courses.append({
                    "course_id": cid,
                    "title":     metadata["title"]
                })
        recommendations[skill] = courses

    return recommendations


def format_courses_for_prompt(courses):
    """
    Converts a list of course dicts into clean text for the LLM prompt.
    Handles prerequisites that may be nested lists or plain strings.
    """

    def flatten(value):
        """Recursively flattens nested lists into a single list of strings."""
        if not value:
            return []
        result = []
        for item in value:
            if isinstance(item, list):
                result.extend(flatten(item))
            else:
                result.append(str(item))
        return result

    lines = []
    for c in courses:
        prerequisites = flatten(c.get("prerequisites") or [])
        only_one      = flatten(c.get("only_one_of_these") or [])
        skills        = flatten(c.get("skills_taught") or [])

        lines.append(f"""Course ID: {c['course_id']}
Title: {c['title']}
Type: {c['course_type']} | Credits: {c['credits']}
Description: {c.get('description', 'N/A')}
Skills Taught: {', '.join(skills) if skills else 'N/A'}
Prerequisites: {', '.join(prerequisites) if prerequisites else 'None'}
Only One Of These: {', '.join(only_one) if only_one else 'N/A'}""")

    return "\n\n---\n\n".join(lines)