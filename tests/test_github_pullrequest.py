from pull_requests import stats

# mocker.patch("pull_requests.stats.get_token", return_value="")


def test_get_pull_requests(mocker):
    def mock_get_pulls(state, sort, base):
        from datetime import datetime, timedelta

        class pull_request_class:
            closed_at = datetime.now()
            created_at = datetime.now() + timedelta(days=-1)
            number = "001"
            title = "pull_request_1"
            merged_at = datetime.now()

        mock_pull_request_1 = pull_request_class()

        mock_pull_request_2 = pull_request_class()
        mock_pull_request_2.number = "002"
        mock_pull_request_2.title = "pull_request_2"
        mock_pull_request_2.created_at = datetime.now() + timedelta(days=-5)
        mock_pull_request_2.merged_at = None

        return [mock_pull_request_1, mock_pull_request_2]

    repository = mocker.patch("github.Repository.Repository")
    mocker.patch("github.Repository.Repository.get_pulls", mock_get_pulls)

    pull_requests = stats.get_closed_pull_requests(repository, default_branch="main")

    assert pull_requests is not None
    assert round(pull_requests["001"]["duration"], 1) == 1.0
    assert round(pull_requests["002"]["duration"], 1) == 5.0
    assert pull_requests["001"]["ending"] == "merged"
    assert pull_requests["002"]["ending"] == "closed"
