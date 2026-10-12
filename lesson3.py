import httpx
from pydantic import BaseModel


class GitHubUser(BaseModel):
    login: str
    name: str | None
    public_repos: int
    followers: int


data = httpx.get("https://api.github.com/users/octocat").json()
user = GitHubUser.model_validate(data)
test = GitHubUser(login="x", name=None, public_repos="5", followers=1)
print(test.public_repos, type(test.public_repos))
print(user.model_dump())