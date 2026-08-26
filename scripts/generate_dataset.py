import json
import os

def generate_catalog():
    domains = {
        "DE": ("Data Engineering", [
            ("101", "Python for Data Science", "Beginner", 10, [], ["Python"]),
            ("102", "Relational Databases & SQL", "Beginner", 15, [], ["SQL", "PostgreSQL"]),
            ("103", "Data Warehousing Fundamentals", "Intermediate", 20, ["DE101", "DE102"], ["ETL", "Data Warehousing"]),
            ("104", "Distributed Computing with PySpark", "Intermediate", 25, ["DE103"], ["PySpark", "Hadoop"]),
            ("105", "Real-Time Streaming with Apache Kafka", "Advanced", 30, ["DE104"], ["Kafka", "Event Streaming"]),
            ("106", "Data Mesh Architecture", "Advanced", 20, ["DE105"], ["Data Governance", "System Architecture"])
        ]),
        "ML": ("Machine Learning", [
            ("101", "Linear Algebra for ML", "Beginner", 12, [], ["Math", "Linear Algebra"]),
            ("102", "Applied Machine Learning", "Intermediate", 18, ["ML101", "DE101"], ["Machine Learning", "Scikit-Learn"]),
            ("103", "Deep Learning & Neural Networks", "Intermediate", 25, ["ML102"], ["PyTorch", "Deep Learning"]),
            ("104", "Natural Language Processing", "Advanced", 30, ["ML103"], ["NLP", "Transformers", "LLMs"]),
            ("105", "MLOps: Deployment & Monitoring", "Advanced", 22, ["ML103"], ["MLOps", "Docker", "FastAPI"])
        ]),
        "WEB": ("Full Stack Web Dev", [
            ("101", "HTML, CSS, and Modern JavaScript", "Beginner", 10, [], ["JavaScript", "HTML/CSS"]),
            ("102", "Frontend Development with React", "Intermediate", 20, ["WEB101"], ["React", "Frontend"]),
            ("103", "Backend Services with Node.js", "Intermediate", 18, ["WEB101"], ["Node.js", "REST API"]),
            ("104", "Full Stack Next.js Architecture", "Advanced", 25, ["WEB102", "WEB103"], ["Next.js", "Full Stack"])
        ])
    }

    courses = []
    for prefix, (domain_name, module_list) in domains.items():
        for item in module_list:
            cid, title, diff, hours, prereqs, skills = item
            courses.append({
                "course_id": f"{prefix}{cid}",
                "title": title,
                "provider": "Coursera / edX",
                "description": f"Hands-on training in {title}. Skills: {', '.join(skills)}.",
                "skills_covered": skills,
                "prerequisites": prereqs,
                "difficulty": diff,
                "est_hours": hours
            })

    os.makedirs("data", exist_ok=True)
    with open("data/full_courses.json", "w") as f:
        json.dump(courses, f, indent=2)

    print(f"Generated {len(courses)} courses in data/full_courses.json")

if __name__ == "__main__":
    generate_catalog()