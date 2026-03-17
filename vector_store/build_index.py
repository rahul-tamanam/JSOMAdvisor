import json
import os
import chromadb
from chromadb.utils import embedding_functions
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def build_courses_index():
    """
    Loads courses.json and builds a ChromaDB collection.
    Each course is stored as a document with its full context.
    Run this once — it persists to disk.
    """
    with open(os.path.join(DATA_DIR, "courses.json")) as f:
        courses = json.load(f)

    # Use the same small model for consistency
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=DB_DIR)

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("courses")
    except:
        pass

    collection = client.create_collection(
        name="courses",
        embedding_function=ef
    )

    documents = []
    metadatas = []
    ids = []

    for course in courses:
        # Build a rich text document for embedding
        # This is what the semantic search indexes
        doc = f"""
Course: {course['course_id']} - {course['title']}
Type: {course['course_type']}
Credits: {course['credits']}
Description: {course.get('description', '')}
Skills Taught: {', '.join(course.get('skills_taught') or [])}
Prerequisites: {course.get('prerequisites') or 'None'}
Only One Of These: {course.get('only_one_of_these') or 'N/A'}
        """.strip()

        # Store full course data as metadata for retrieval
        metadatas.append({
            "course_id":        course["course_id"],
            "title":            course["title"],
            "credits":          str(course["credits"]),
            "course_type":      course["course_type"],
            "description":      course.get("description") or "",
            "prerequisites":    json.dumps(course.get("prerequisites") or []),
            "only_one_of_these": json.dumps(course.get("only_one_of_these") or []),
            "skills_taught":    json.dumps(course.get("skills_taught") or [])
        })

        documents.append(doc)
        ids.append(course["course_id"])

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Courses index built — {len(courses)} courses indexed")
    return collection


def build_skills_index():
    """
    Loads skills.json and builds a ChromaDB collection.
    """
    with open(os.path.join(DATA_DIR, "skills.json")) as f:
        skills = json.load(f)

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    client = chromadb.PersistentClient(path=DB_DIR)

    try:
        client.delete_collection("skills")
    except:
        pass

    collection = client.create_collection(
        name="skills",
        embedding_function=ef
    )

    documents = []
    metadatas = []
    ids = []

    for i, role in enumerate(skills):
        doc = f"""
Job Title: {role['job_title']}
Technical Skills: {', '.join(role['technical_skills'])}
Soft Skills: {', '.join(role['soft_skills'])}
        """.strip()

        metadatas.append({
            "job_title":         role["job_title"],
            "technical_skills":  json.dumps(role["technical_skills"]),
            "soft_skills":       json.dumps(role["soft_skills"])
        })

        documents.append(doc)
        ids.append(str(i))

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Skills index built — {len(skills)} job roles indexed")
    return collection


if __name__ == "__main__":
    print("Building vector indices...\n")
    build_courses_index()
    build_skills_index()
    print("\nDone. Indices saved to vector_store/chroma_db/")