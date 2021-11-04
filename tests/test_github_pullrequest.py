from pull_requests import app


def test_get_pr_return_none():
    ret = app.pr(repo="pact-foundation/pact-workshop-js")
    assert ret is not None
