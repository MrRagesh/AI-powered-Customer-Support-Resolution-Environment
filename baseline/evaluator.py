"""Score aggregation for baseline runs."""
from typing import List


class Evaluator:
    def aggregate(self, results: List[dict]) -> dict:
        if not results:
            return {"mean_score": 0.0, "pass_rate": 0.0, "results": []}
        scores  = [r.get("score", 0) for r in results]
        passed  = [r.get("passed", False) for r in results]
        return {
            "mean_score":    round(sum(scores) / len(scores), 2),
            "pass_rate":     round(sum(passed) / len(passed), 2),
            "min_score":     min(scores),
            "max_score":     max(scores),
            "total_tasks":   len(results),
            "results":       results,
        }
