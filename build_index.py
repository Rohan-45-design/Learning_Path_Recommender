from rag.load_data import load_courses
from rag.vector_store import CourseVectorStore

df = load_courses("data/Coursera.csv")
store = CourseVectorStore()
store.add_courses_batch(df)

print("Courses indexed:", len(df))
