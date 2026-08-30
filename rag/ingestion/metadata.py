from typing import List, Dict, Set
from rag.ingestion.loader import PrerequisiteModel

class MetadataManager:
    def __init__(self, prerequisites: List[PrerequisiteModel]):
        self.prereq_graph: Dict[str, Set[str]] = {}
        self._build_prereq_graph(prerequisites)

    def _build_prereq_graph(self, prerequisites: List[PrerequisiteModel]):
        for item in prerequisites:
            target = item.target_skill.strip()
            prereq = item.prerequisite_skill.strip()
            if target not in self.prereq_graph:
                self.prereq_graph[target] = set()
            self.prereq_graph[target].add(prereq)

    def get_prerequisites_for_skill(self, skill_name: str) -> Set[str]:
        return self.prereq_graph.get(skill_name.strip(), set())

    def is_prerequisite_satisfied(self, resource_prereqs: List[str], learner_skills: List[str]) -> bool:
        learner_set = {s.strip().lower() for s in learner_skills}
        for req in resource_prereqs:
            req_clean = req.strip().lower()
            if req_clean != "none" and req_clean not in learner_set:
                return False
        return True

    def calculate_prerequisite_readiness(self, resource_prereqs: List[str], learner_skills: List[str]) -> float:
        """Returns ratio of satisfied prerequisites (1.0 if no prerequisites)."""
        clean_prereqs = [p.strip().lower() for p in resource_prereqs if p.strip().lower() != "none"]
        if not clean_prereqs:
            return 1.0
        learner_set = {s.strip().lower() for s in learner_skills}
        satisfied = sum(1 for p in clean_prereqs if p in learner_set)
        return satisfied / len(clean_prereqs)
