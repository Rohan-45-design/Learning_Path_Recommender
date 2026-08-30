import time
import numpy as np
from rag.pipeline.rag import RAGPipeline

def dcg_at_k(r, k=3):
    r = np.asarray(r, dtype=float)[:k]
    if not r.size:
        return 0.0
    return np.sum(r / np.log2(np.arange(2, r.size + 2)))

def ndcg_at_k(r, k=3):
    dcg_max = dcg_at_k(sorted(r, reverse=True), k)
    if not dcg_max:
        return 0.0
    return dcg_at_k(r, k) / dcg_max

def run_comprehensive_evaluation():
    pipeline = RAGPipeline()

    scenarios = [
        {
            "id": "Scenario 1 (AI Engineer)",
            "query": "What should I learn next?",
            "profile": {"goal": "AI Engineer", "current_skills": ["Python", "Machine Learning"], "level": "Intermediate"},
            "target_skill": "deep_learning"
        },
        {
            "id": "Scenario 2 (GenAI Engineer)",
            "query": "Recommend next steps for generative AI",
            "profile": {"goal": "GenAI Engineer", "current_skills": ["Python", "Machine Learning", "Deep Learning"], "level": "Intermediate"},
            "target_skill": "transformers"
        },
        {
            "id": "Scenario 3 (Data Scientist)",
            "query": "What course should I take for data science?",
            "profile": {"goal": "Data Scientist", "current_skills": ["Python", "Statistics"], "level": "Intermediate"},
            "target_skill": "sql"
        },
        {
            "id": "Scenario 4 (NLP Specialist)",
            "query": "Next step for NLP career",
            "profile": {"goal": "NLP Engineer", "current_skills": ["Python", "Machine Learning"], "level": "Intermediate"},
            "target_skill": "deep_learning"
        },
        {
            "id": "Scenario 5 (CV Specialist)",
            "query": "Computer vision learning roadmap",
            "profile": {"goal": "Computer Vision Engineer", "current_skills": ["Python", "Machine Learning"], "level": "Intermediate"},
            "target_skill": "deep_learning"
        },
        {
            "id": "Scenario 6 (MLOps Engineer)",
            "query": "How to deploy ML models to production?",
            "profile": {"goal": "ML Engineer", "current_skills": ["Python", "Machine Learning", "Deep Learning"], "level": "Intermediate"},
            "target_skill": "fastapi"
        },
        {
            "id": "Scenario 7 (Beginner Python Learner)",
            "query": "I just learned basic Python, what next?",
            "profile": {"goal": "Data Scientist", "current_skills": ["Python"], "level": "Beginner"},
            "target_skill": "statistics"
        },
        {
            "id": "Scenario 8 (Advanced AI Architect)",
            "query": "Advanced AI topics for experienced practitioner",
            "profile": {"goal": "GenAI Engineer", "current_skills": ["Python", "Machine Learning", "Deep Learning", "Transformers"], "level": "Advanced"},
            "target_skill": "llm"
        },
        {
            "id": "Scenario 9 (Cloud & AI Integration)",
            "query": "How to integrate AI services on cloud?",
            "profile": {"goal": "Software Engineer", "current_skills": ["Python", "SQL"], "level": "Intermediate"},
            "target_skill": "fastapi"
        },
        {
            "id": "Scenario 10 (Adaptive Feedback Step)",
            "query": "Next step after completing Deep Learning",
            "profile": {"goal": "AI Engineer", "current_skills": ["Python", "Machine Learning", "Deep Learning"], "level": "Intermediate"},
            "target_skill": "neural_networks"
        }
    ]

    print("\n" + "=" * 80)
    print("PATHAI RAG COMPREHENSIVE BENCHMARK EVALUATION (10 SCENARIOS)")
    print("Metrics: Target Skill Hit Rate %, NDCG@3, Prerequisite Violation Rate %, Precision@3")
    print("=" * 80)

    total_target_hits = 0
    total_ndcg = 0.0
    total_precision = 0.0
    total_latency = 0.0
    total_prereq_violations = 0
    total_recommendations_count = 0

    for scenario in scenarios:
        t0 = time.time()
        response = pipeline.query(
            query=scenario["query"],
            learner_profile=scenario["profile"],
            top_k_retrieval=15,
            top_k_final=3
        )
        latency = (time.time() - t0) * 1000
        total_latency += latency

        recs = response.recommendations
        total_recommendations_count += len(recs)
        target = scenario["target_skill"].lower()

        rel_scores = []
        top1_hit = False

        for idx, r in enumerate(recs):
            if r.get("prereq_violations", 0) > 0:
                total_prereq_violations += r.get("prereq_violations", 0)

            skills_str = r.get("course_name", "").lower() + " " + r.get("url", "").lower() + " " + r.get("difficulty", "").lower()
            is_match = target.replace("_", " ") in skills_str or target in skills_str or r.get("target_match_score", 0) > 0.5

            if idx == 0 and is_match:
                top1_hit = True

            rel = 1.0 if is_match else 0.0
            rel_scores.append(rel)

        if top1_hit:
            total_target_hits += 1

        ndcg_val = ndcg_at_k(rel_scores, k=3)
        total_ndcg += ndcg_val
        precision_val = sum(rel_scores) / max(len(recs), 1)
        total_precision += precision_val

        hit_str = "[HIT]" if top1_hit else "[MISS]"
        print(f"\n{hit_str} [{scenario['id']}] Target Skill: '{target}' | Query: '{scenario['query']}'")
        print(f"   Learner Goal: {scenario['profile']['goal']} | Skills: {scenario['profile']['current_skills']}")
        print(f"   Latency: {round(latency, 1)} ms | Confidence: {response.confidence}")
        print("   Top Recommendations:")
        for idx, r in enumerate(recs, 1):
            why = "; ".join(r.get("why_recommended", [])[:2])
            print(f"     {idx}. {r['course_name']} ({r['university']}) [Score: {r['score']}]")
            if why:
                print(f"        Why: {why}")
        print(f"   Target Skill Hit: {top1_hit} | NDCG@3: {round(ndcg_val, 2)} | Precision@3: {round(precision_val, 2)}")

    target_hit_rate = round((total_target_hits / len(scenarios)) * 100, 1)
    avg_ndcg = round(total_ndcg / len(scenarios), 2)
    avg_prec = round(total_precision / len(scenarios), 2)
    avg_lat = round(total_latency / len(scenarios), 1)
    prereq_violation_rate = round((total_prereq_violations / max(total_recommendations_count, 1)) * 100, 2)

    print("\n" + "=" * 80)
    print("FINAL BENCHMARK EVALUATION SUMMARY Across 10 SCENARIOS")
    print(f"• Target Skill Hit Rate @ Top-1: {target_hit_rate}%")
    print(f"• Average NDCG@3: {avg_ndcg}")
    print(f"• Average Precision@3: {avg_prec}")
    print(f"• Prerequisite Violation Rate: {prereq_violation_rate}% (Target: 0.00%)")
    print(f"• Average Query Latency: {avg_lat} ms")
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_evaluation()
