import json
import os
import chromadb
from sentence_transformers import SentenceTransformer

def run_ingestion():
    chroma_path = "./chroma_db"
    client = chromadb.PersistentClient(path=chroma_path)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="course_catalog")

    with open("data/full_courses.json", "r") as f:
        courses = json.load(f)

    documents = []
    metadatas = []
    ids = []

    for course in courses:
        text_content = f"Title: {course['title']}. Description: {course['description']}. Skills: {', '.join(course['skills_covered'])}"
        documents.append(text_content)
        ids.append(course['course_id'])
        metadatas.append({
            "title": course['title'],
            "difficulty": course['difficulty'],
            "skills": ", ".join(course['skills_covered']),
            "prerequisites": ", ".join(course['prerequisites'])
        })

    embeddings = model.encode(documents).tolist()
    collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Ingested {len(courses)} courses into ChromaDB at '{chroma_path}'!")

if __name__ == "__main__":
    run_ingestion()