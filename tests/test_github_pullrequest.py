from pull_requests import app


def test_get_pr():
    ret = app.pr(repo="https://github.com/pact-foundation/pact-workshop-js")
    assert ret is None
