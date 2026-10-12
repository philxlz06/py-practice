import logging

import httpx
from pydantic import BaseModel, ValidationError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class GitHubUser(BaseModel):
    login: str
    public_repos: int


def fetch_user(username: str) -> GitHubUser | None:
    try:
        response = httpx.get(f"https://api.github.com/users/{username}", timeout=10)
        response.raise_for_status()
        return GitHubUser.model_validate(response.json())
    except httpx.HTTPStatusError as e:
        logger.warning("GitHub returned %s for %s", e.response.status_code, username)
    except httpx.RequestError as e:
        logger.error("Network problem: %s", e)
    except ValidationError as e:
        logger.error("Unexpected data shape: %s", e)
    return None


for name in ["octocat", "this-user-does-not-exist-12345"]:
    user = fetch_user(name)
    if user:
        logger.info("Got %s with %d repos", user.login, user.public_repos)