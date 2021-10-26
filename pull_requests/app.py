import pandas as pd

import stats

input_file_excel = "input/GitHub Repositories.xlsx"
df = pd.read_excel(input_file_excel, sheet_name="repositories")

repositories = pd.DataFrame()
for index, repo in df.iterrows():

    kwargs = {"repo_name": repo["Repository"]}
    ret = stats.main(**kwargs)
    if ret is not None:
        repositories = repositories.append(ret)

repositories.to_excel(
    "export/pull_requests_stats.xlsx", sheet_name="pull_request_stats", index=False
)
