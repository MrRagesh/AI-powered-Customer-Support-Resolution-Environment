"""
Baseline inference script — runs all tasks and reports scores.

Usage:
    python -m baseline.run --url http://localhost:7860 --api-key YOUR_KEY
"""
import asyncio
import argparse
import json
import httpx
from baseline.agent import BaselineAgent
from baseline.evaluator import Evaluator
from app.core.constants import TASK_IDS, TaskDifficulty, ActionType


async def run_episode(client: httpx.AsyncClient, task_id: str, agent: BaselineAgent) -> dict:
    # Reset
    r = await client.post("/env/reset", json={"task_id": task_id})
    r.raise_for_status()
    data       = r.json()
    session_id = data["session_id"]
    ticket_text = data["state"].get("ticket", {}).get("text", "")

    actions = agent.get_actions(task_id, ticket_text)
    done    = False
    for action in actions:
        if done:
            break
        r = await client.post("/env/step", json={"session_id": session_id, "action": action})
        r.raise_for_status()
        step_data = r.json()
        done = step_data["done"]

    # Grade
    r = await client.post("/grader", json={"session_id": session_id})
    r.raise_for_status()
    grade = r.json()
    return grade


async def main(url: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}"}
    agent   = BaselineAgent()
    eval_   = Evaluator()
    results = []

    async with httpx.AsyncClient(base_url=url, headers=headers, timeout=60.0) as client:
        for task_id in TASK_IDS.values():
            print(f"  Running task: {task_id}...")
            try:
                result = await run_episode(client, task_id, agent)
                results.append(result)
                print(f"    score={result['score']}, passed={result['passed']}")
            except Exception as e:
                print(f"    ERROR: {e}")
                results.append({"task_id": task_id, "score": 0, "passed": False, "error": str(e)})

    summary = eval_.aggregate(results)
    print("\n" + "="*50)
    print(f"BASELINE RESULTS")
    print("="*50)
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url",     default="http://localhost:7860")
    parser.add_argument("--api-key", default="changeme-dev-key-only-32chars!!")
    args = parser.parse_args()
    asyncio.run(main(args.url, args.api_key))
