from pathlib import Path

import httpx
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    github_username: str


class GitHubUser(BaseModel):
    login: str
    public_repos: int


CACHE = Path("user_cache.json")


def get_user(username: str) -> GitHubUser:
    if CACHE.exists():
        print("loading from cache")
        return GitHubUser.model_validate_json(CACHE.read_text())

    print("fetching from GitHub")
    response = httpx.get(f"https://api.github.com/users/{username}", timeout=10)
    response.raise_for_status()
    user = GitHubUser.model_validate(response.json())
    CACHE.write_text(user.model_dump_json(indent=2))
    return user


settings = Settings()
user = get_user(settings.github_username)
print(user)