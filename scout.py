import asyncio
import logging
from datetime import datetime

import httpx
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

REPOS = [
    "anthropics/skills",
    "NousResearch/hermes-agent",
    "firecrawl/firecrawl",
    "obra/superpowers",
    "anomalyco/opencode",
    "fake-owner/fake-repo",
]


class RepoStats(BaseModel):
    full_name: str
    stargazers_count: int
    open_issues_count: int
    language: str | None
    pushed_at: datetime


async def fetch_repo(client: httpx.AsyncClient, full_name: str, semaphore: asyncio.Semaphore) -> RepoStats | None:
    async with semaphore:
        try:
            response = await client.get(f"/repos/{full_name}")
            response.raise_for_status()
            return RepoStats.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            logger.warning("%s failed: %s", full_name, e.response.status_code)
        except httpx.RequestError as e:
            logger.error("%s network error: %s", full_name, e)
        except ValidationError as e:
            logger.error("%s unexpected data: %s", full_name, e)
    return None


async def main() -> None:
    semaphore = asyncio.Semaphore(3)
    async with httpx.AsyncClient(
        base_url="https://api.github.com",
        headers={"User-Agent": "py-practice"},
        timeout=10,
    ) as client:
        results = await asyncio.gather(*(fetch_repo(client, r, semaphore) for r in REPOS))

    repos = [r for r in results if r is not None]
    repos.sort(key=lambda r: r.stargazers_count, reverse=True)

    for rank, repo in enumerate(repos, start=1):
        logger.info(
            "#%d %s | %d stars | %d open issues | %s | last push %s",
            rank, repo.full_name, repo.stargazers_count,
            repo.open_issues_count, repo.language, repo.pushed_at.date(),
        )


asyncio.run(main())