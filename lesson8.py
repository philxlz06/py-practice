import time
from dataclasses import dataclass
from functools import wraps

import httpx


@dataclass
class Repo:
    name: str
    stars: int


class GitHubClient:
    def __init__(self, username: str):
        self.username = username
        self.client = httpx.Client(base_url="https://api.github.com", timeout=10)

    def get_repos(self) -> list[Repo]:
        response = self.client.get(f"/users/{self.username}/repos", params={"sort": "updated"})
        response.raise_for_status()
        return [Repo(name=r["name"], stars=r["stargazers_count"]) for r in response.json()]

    def close(self) -> None:
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.perf_counter() - start:.2f}s")
        return result
    return wrapper


@timed
def show_repos(username: str) -> None:
    with GitHubClient(username) as gh:
        for repo in gh.get_repos()[:3]:
            print(repo)


show_repos("philxlz06")
show_repos("octocat")