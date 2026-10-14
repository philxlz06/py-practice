import httpx

with httpx.Client(
    base_url="https://api.github.com",
    headers={"Accept": "application/vnd.github+json", "User-Agent": "py-practice"},
    timeout=10,
) as client:
    response = client.get("/search/repositories", params={"q": "agent", "sort": "stars", "per_page": 10})
    response.raise_for_status()

    for repo in response.json()["items"]:
        print(repo["full_name"], repo["stargazers_count"])

    print("requests left this hour:", response.headers["x-ratelimit-remaining"])

response = httpx.post("https://httpbin.org/post", json={"name": "philip", "project": "py-practice"}, timeout=10)
print(response.status_code, response.text[:200])
response.raise_for_status()
print(response.json()["json"])
