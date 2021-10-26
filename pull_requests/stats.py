import os
import statistics
import sys
from datetime import datetime, timedelta

import numpy
import pandas as pd
from github import Github

PATH_CLOSED_FILES = "export/raw/closed/"
PATH_MERGED_FILES = "export/raw/merged/"
PATH_OPEN_FILES = "export/raw/open/"
PATH_TOTAL_FILES = "export/raw/total/"
GITHUB_URL = "https://github.com/"


def get_token():
    try:
        "GITHUB_AUTH_TOKEN" in os.environ
    except KeyError:
        print("Please set the environment variable GITHUB_AUTH_TOKEN")
        sys.exit(1)
    return os.environ["GITHUB_OS_AUTH_TOKEN"]


def get_repository(repository_name):
    token = get_token()
    github_connector = Github(token)

    try:
        repository = github_connector.get_repo(repository_name)
        return repository
    except Exception:
        pass
    return None


def get_pull_requests_from_repository(repository):
    pull_requests = repository.get_pulls(state="all", sort="created")

    pull_requests_processed = {}
    for pull_request in pull_requests:
        pr_details = {}

        if pull_request.state == "open":
            diff_dt = datetime.now() - pull_request.created_at
            pr_duration_open_days = (
                diff_dt.total_seconds() / timedelta(days=1).total_seconds()
            )
            pr_details["duration"] = pr_duration_open_days
            pr_details["status"] = "open"

        if pull_request.state == "closed":
            diff_dt = pull_request.closed_at - pull_request.created_at
            pr_duration_closed_days = (
                diff_dt.total_seconds() / timedelta(days=1).total_seconds()
            )
            pr_details["duration"] = pr_duration_closed_days
            pr_details["status"] = "merged" if pull_request.is_merged() else "closed"
            pr_details["closed"] = pull_request.closed_at

        pr_details["number"] = pull_request.number
        pr_details["title"] = pull_request.title
        pr_details["created"] = pull_request.created_at
        pr_details["last_updated"] = pull_request.updated_at
        pr_details["url"] = (
            GITHUB_URL + repository.full_name + "/pull/" + str(pull_request.number)
        )

        pull_requests_processed[pull_request.number] = pr_details

    return pull_requests_processed


def generate_statistics(pull_requests):
    amount_pull_requests = len(pull_requests)
    last_date_pr = max(
        [pr_values["last_updated"] for pr_values in pull_requests.values()]
    )
    max_duration = max([pr_values["duration"] for pr_values in pull_requests.values()])
    min_duration = min([pr_values["duration"] for pr_values in pull_requests.values()])

    durations = [pr_values["duration"] for pr_values in pull_requests.values()]
    percentile_75th = numpy.percentile(durations, 75)
    percentile_95th = numpy.percentile(durations, 95)
    median = statistics.median(durations)
    average = statistics.mean(durations)
    mode = statistics.mode(durations)

    summary = {
        "pull_requests": amount_pull_requests,
        "max_duration": round(max_duration, 3),
        "min_duration": round(min_duration, 3),
        "percentile_75th": round(percentile_75th, 3),
        "percentile_95th": round(percentile_95th, 3),
        "median": round(median, 3),
        "average": round(average, 3),
        "mode": round(mode, 3),
        "last_date_pr": last_date_pr,
    }

    return summary


def main(**kawrgs):
    repo_name = kawrgs["repo_name"]
    xls_file_name = repo_name.split("/")[1] + ".xlsx"

    repository = get_repository(repo_name)

    if repository is None:
        return None

    pull_requests = get_pull_requests_from_repository(repository)

    if len(pull_requests) == 0:
        df_summary = pd.DataFrame({"repository": [repo_name], "status": ["Not found"]})
        return df_summary

    df_pull_requests = pd.DataFrame.from_dict(pull_requests, orient="index")
    df_pull_requests.to_excel(
        PATH_TOTAL_FILES + xls_file_name, sheet_name="pull_requests", index=False
    )

    pull_requests_open = dict(
        (
            pull_request
            for pull_request in pull_requests.items()
            if pull_request[1]["status"] == "open"
        )
    )
    pull_requests_closed = dict(
        (
            pull_request
            for pull_request in pull_requests.items()
            if pull_request[1]["status"] == "closed"
        )
    )
    pull_requests_merged = dict(
        (
            pull_request
            for pull_request in pull_requests.items()
            if pull_request[1]["status"] == "merged"
        )
    )

    df_summary = pd.DataFrame()

    if len(pull_requests_open) > 0:
        df_open_pull_requests = pd.DataFrame.from_dict(
            pull_requests_open, orient="index"
        )
        df_open_pull_requests.to_excel(
            PATH_OPEN_FILES + xls_file_name, sheet_name="pull_requests", index=False
        )

        pr_open_summary = {"repository": repo_name, "status": "Open"}
        pr_open_summary.update(generate_statistics(pull_requests_open))
        df_summary = df_summary.append([pr_open_summary])

    if len(pull_requests_closed) > 0:
        df_closed_pull_requests = pd.DataFrame.from_dict(
            pull_requests_closed, orient="index"
        )
        df_closed_pull_requests.to_excel(
            PATH_CLOSED_FILES + xls_file_name, sheet_name="pull_requests", index=False
        )

        pr_closed_summary = {"repository": repo_name, "status": "Closed"}
        pr_closed_summary.update(generate_statistics(pull_requests_closed))
        df_summary = df_summary.append([pr_closed_summary])

    if len(pull_requests_merged) > 0:
        df_merged_pull_requests = pd.DataFrame.from_dict(
            pull_requests_merged, orient="index"
        )
        df_merged_pull_requests.to_excel(
            PATH_MERGED_FILES + xls_file_name, sheet_name="pull_requests", index=False
        )

        pr_merged_summary = {"repository": repo_name, "status": "Merged"}
        pr_merged_summary.update(generate_statistics(pull_requests_merged))
        df_summary = df_summary.append([pr_merged_summary])

    return df_summary
