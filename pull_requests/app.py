import typer

import stats

app = typer.Typer()


@app.command()
def pr(repo: str):
    ret = stats.main(repo)
    return ret.to_csv()


if __name__ == "__main__":
    app()
