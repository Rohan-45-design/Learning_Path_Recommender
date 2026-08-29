"""Seed script to import data/mock_courses.json into SQLite database."""
from backend.database import init_db, seed_mock_courses

if __name__ == "__main__":
    print("Initializing database tables...")
    init_db()
    print("Seeding courses from data/mock_courses.json...")
    count = seed_mock_courses()
    print(f"Successfully seeded {count} new course(s) into database.")
