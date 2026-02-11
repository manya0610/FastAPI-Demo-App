import asyncio
import httpx
import time
import json
import random
import string

SERVER_URL = "http://localhost:3333/webhook"
CONCURRENCY = 50   # number of concurrent workers
REQUESTS = 1000   # total number of requests

# Generate a random JSON payload
def make_payload():
    return {
        "id": "".join(random.choices(string.ascii_letters + string.digits, k=8)),
        "timestamp": time.time(),
        "data": {
            "value": random.randint(1, 1000),
            "message": "hello world"
        }
    }

async def worker(client: httpx.AsyncClient, task_id: int):
    payload = make_payload()
    try:
        res = await client.post(SERVER_URL, json=payload, timeout=10)
        return (task_id, res.status_code, res.text.strip())
    except Exception as e:
        return (task_id, "ERR", str(e))

async def run_load_test():
    results = []
    async with httpx.AsyncClient() as client:
        sem = asyncio.Semaphore(CONCURRENCY)
        tasks = []

        async def bound_worker(i):
            async with sem:
                return await worker(client, i)

        for i in range(REQUESTS):
            tasks.append(asyncio.create_task(bound_worker(i)))

        for fut in asyncio.as_completed(tasks):
            result = await fut
            results.append(result)
            if len(results) % 50 == 0:
                print(f"Completed {len(results)} requests")

    return results

if __name__ == "__main__":
    start = time.time()
    results = asyncio.run(run_load_test())
    duration = time.time() - start

    # Stats
    successes = sum(1 for r in results if r[1] == 200)
    failures = len(results) - successes

    print("\n--- Load Test Report ---")
    print(f"Total requests: {len(results)}")
    print(f"Successes:      {successes}")
    print(f"Failures:       {failures}")
    print(f"Duration:       {duration:.2f}s")
    print(f"RPS:            {len(results)/duration:.2f}")
