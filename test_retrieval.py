from rag.pipeline import RAGPipeline

pipeline = RAGPipeline()

learner_profile = {
    "goal": "GenAI Engineer",
    "current_skills": ["Python", "Machine Learning"],
    "level": "Intermediate"
}

query = "What should I learn next?"

print("\n" + "=" * 70)
print(f"QUERY: '{query}'")
print(f"LEARNER PROFILE: Goal = {learner_profile['goal']} | Skills = {learner_profile['current_skills']}")
print("=" * 70)

response = pipeline.query(
    query,
    learner_profile=learner_profile,
    requested_why_not_skill="RAG"
)

print(f"\nTARGET NEXT SKILL: {response.next_skill}")
print(f"SKILL GAPS IDENTIFIED: {response.skill_gaps}")

print("\n--- STRUCTURED LEARNING PATH MILESTONES ---")
for m in response.learning_path:
    status_icon = "--> [NEXT STEP]" if m["status"] == "next" else f"    [{m['status'].upper()}]"
    print(f"{status_icon} Stage {m['stage']}: {m['display_name']} (Prerequisites Met: {m['prerequisites_met']})")

print("\n--- TOP RERANKED COURSE RECOMMENDATIONS ---")
for idx, rec in enumerate(response.recommendations, 1):
    print(f"\n[{idx}] Course: {rec['course_name']}")
    print(f"    University: {rec['university']} | Difficulty: {rec['difficulty']} | Score: {rec['score']}")
    print(f"    Why Recommended: {'; '.join(rec['why_recommended'])}")
    print(f"    URL: {rec['url']}")

print("\n--- EXPLAINABLE REASONING: WHY NOT RAG YET? ---")
if response.why_not_explanation:
    print(f"Status: {response.why_not_explanation['status']}")
    print(f"Explanation: {response.why_not_explanation['explanation']}")

print("\n--- GROUNDED AI MENTOR ANSWER ---")
print(response.answer)
