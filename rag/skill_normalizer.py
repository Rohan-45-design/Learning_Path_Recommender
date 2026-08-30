import re
from typing import List, Union

SKILL_ALIASES = {
    "python programming": "python",
    "python programming language": "python",
    "python language": "python",
    "python": "python",

    "machine learning": "machine_learning",
    "machine learning algorithms": "machine_learning",
    "applied machine learning": "machine_learning",
    "ml": "machine_learning",

    "deep learning": "deep_learning",
    "deep neural networks": "deep_learning",
    "neural networks": "deep_learning",

    "natural language processing": "nlp",
    "nlp": "nlp",

    "computer vision": "computer_vision",
    "cv": "computer_vision",

    "artificial intelligence": "ai",
    "ai": "ai",

    "generative ai": "generative_ai",
    "gen ai": "generative_ai",

    "large language models": "llm",
    "large language model": "llm",
    "llm": "llm",

    "transformers": "transformers",
    "transformer": "transformers",

    "retrieval augmented generation": "rag",
    "retrieval-augmented generation": "rag",
    "rag": "rag",

    "sql": "sql",
    "structured query language": "sql",

    "statistics": "statistics",
    "general statistics": "statistics",

    "docker": "docker",
    "fastapi": "fastapi",
    "cloud computing": "cloud",
    "amazon web services": "aws",
    "aws": "aws",
    "microsoft azure": "azure",
    "azure": "azure",
    "google cloud platform": "gcp",
    "gcp": "gcp",
}

def normalize_skill(skill: str) -> str:
    skill = skill.strip().lower()
    skill = re.sub(r"\s+", " ", skill)
    return SKILL_ALIASES.get(skill, skill)

def normalize_skills(skills: Union[str, List[str]]) -> List[str]:
    if isinstance(skills, str):
        skills = re.split(r"[,;|]|\s\s+", skills)

    result = []
    for skill in skills:
        cleaned = skill.strip()
        if cleaned:
            result.append(normalize_skill(cleaned))

    # Return unique set ordered
    seen = set()
    unique = []
    for s in result:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    return unique
