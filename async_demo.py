import asyncio
import time

import httpx

USERS = ["octocat", "torvalds", "gvanrossum", "tiangolo", "philxlz06"]


def fetch_all_sync():
    with httpx.Client(timeout=10) as client:
        for user in USERS:
            response = client.get(f"https://api.github.com/users/{user}")
            print(user, response.status_code)


async def fetch_one(client: httpx.AsyncClient, user: str):
    response = await client.get(f"https://api.github.com/users/{user}")
    print(user, response.status_code)


async def fetch_all_async():
    async with httpx.AsyncClient(timeout=10) as client:
        await asyncio.gather(*(fetch_one(client, user) for user in USERS))


start = time.perf_counter()
fetch_all_sync()
print(f"sync took {time.perf_counter() - start:.2f}s\n")

start = time.perf_counter()
asyncio.run(fetch_all_async())
print(f"async took {time.perf_counter() - start:.2f}s")
