import typer

import pull_requests.stats as stats

app = typer.Typer()


@app.command()
def pr(repo: str) -> str:
    ret = stats.main(repo)
    return ret.to_csv() if ret is not None else None


if __name__ == "__main__":
    app()
