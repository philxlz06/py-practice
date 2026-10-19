
import asyncio
import logging
import time
from datetime import datetime
 
import httpx
from pydantic import BaseModel, ValidationError
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
 
# Logging setup: show INFO and above, hide httpx's routine request lines
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
 
 
# Layer 2: the shape of repo data we keep (GitHub sends ~80 fields)
class RepoStats(BaseModel):
    full_name: str
    stargazers_count: int
    open_issues_count: int
    language: str | None
    pushed_at: datetime
 
 
# Layer 4: which failures are temporary and worth retrying
def is_temporary(e: BaseException) -> bool:
    if isinstance(e, httpx.RequestError):
        return True
    return isinstance(e, httpx.HTTPStatusError) and e.response.status_code in (429, 500, 502, 503, 504)
 
 
# Layer 4: one request, retried up to 3 times with backoff on temporary failures
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=1, max=8),
    retry=retry_if_exception(is_temporary),
    reraise=True,
)
async def get_repo_json(client: httpx.AsyncClient, full_name: str) -> dict:
    response = await client.get(f"/repos/{full_name}")
    response.raise_for_status()
    return response.json()
 
 
# Layers 1-3: fetch one repo, at most 3 at a time, never crashing the others
async def fetch_repo(client: httpx.AsyncClient, full_name: str, semaphore: asyncio.Semaphore) -> RepoStats | None:
    async with semaphore:
        try:
            data = await get_repo_json(client, full_name)
            return RepoStats.model_validate(data)
        except httpx.HTTPStatusError as e:
            logger.warning("%s failed: %s", full_name, e.response.status_code)
        except httpx.RequestError as e:
            logger.error("%s network error: %s", full_name, e)
        except ValidationError as e:
            logger.error("%s unexpected data: %s", full_name, e)
    return None
 
 
async def main() -> None:
    start = time.perf_counter()
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
            rank,
            repo.full_name,
            repo.stargazers_count,
            repo.open_issues_count,
            repo.language,
            repo.pushed_at.date(),
        )
 
    # Layer 5: summary
    failed = len(REPOS) - len(repos)
    logger.info("%d succeeded, %d failed, took %.2fs", len(repos), failed, time.perf_counter() - start)
 
 
if __name__ == "__main__":
    asyncio.run(main())