"""Validate OpenEnv API compliance."""
import asyncio, json
import httpx


async def validate(url: str, api_key: str):
    headers = {"Authorization": f"Bearer {api_key}"}
    results = {}

    async with httpx.AsyncClient(base_url=url, headers=headers, timeout=30.0) as c:
        # 1. Health
        r = await c.get("/health")
        results["health"] = r.status_code == 200

        # 2. List tasks
        r = await c.get("/tasks")
        results["list_tasks"] = r.status_code == 200 and len(r.json().get("tasks", [])) >= 3

        # 3. Reset
        r = await c.post("/env/reset", json={"task_id": "support-easy-v1"})
        results["reset"] = r.status_code == 200
        session_id = r.json().get("session_id")

        # 4. Step
        r = await c.post("/env/step", json={
            "session_id": session_id,
            "action": {"type": "classify", "content": "refund issue"}
        })
        results["step"] = r.status_code == 200

        # 5. State
        r = await c.get(f"/env/state/{session_id}")
        results["state"] = r.status_code == 200

        # 6. Grader
        r = await c.post("/grader", json={"session_id": session_id})
        results["grader"] = r.status_code == 200

        # 7. Baseline
        r = await c.post("/baseline")
        results["baseline"] = r.status_code == 200

    all_pass = all(results.values())
    print("\nOpenEnv Validation Results")
    print("=" * 40)
    for k, v in results.items():
        status = "✅ PASS" if v else "❌ FAIL"
        print(f"  {k:25s} {status}")
    print("=" * 40)
    print(f"  Overall: {'✅ ALL PASS' if all_pass else '❌ SOME FAILURES'}")
    return all_pass


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--url",     default="http://localhost:7860")
    p.add_argument("--api-key", default="changeme-dev-key-only-32chars!!")
    args = p.parse_args()
    ok = asyncio.run(validate(args.url, args.api_key))
    exit(0 if ok else 1)
