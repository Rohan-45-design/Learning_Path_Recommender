def create_course_document(row) -> str:
    return f"""
Course: {row['course_name']}

Provider: {row['university']}

Difficulty: {row['difficulty_level']}

Rating: {row['course_rating']}

Skills taught:
{row['skills']}

Course description:
{row['course_description']}
""".strip()
