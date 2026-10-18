import httpx

response = httpx.get("https://api.github.com/users/philxlz06/repos", params={"sort": "updated"}, timeout = 10)
response.raise_for_status()
data = response.json()
for repo in data:
    print(repo["name"])