import httpx


def main():
    response = httpx.get("https://api.github.com/users/octocat")
    data = response.json()
    print(data["name"])


if __name__ == "__main__":
    main()
