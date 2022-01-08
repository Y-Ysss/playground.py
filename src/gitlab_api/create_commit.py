import http.client
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Tuple
from zipfile import ZipFile

from get_gitlab_info import GitLabInfo


def req(request_url: str, headers: dict, data: str = None) -> Tuple[str, http.client.HTTPMessage]:
    request = urllib.request.Request(request_url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request) as r:
            return r.read(), r.headers

    except urllib.error.HTTPError as err:
        print(err.code, err.reason)
        print(json.loads(err.read()))
        raise
    except:
        raise


def get_tree_info(gitlab_info: GitLabInfo) -> list:
    # https://docs.gitlab.com/ee/api/repositories.html#list-repository-tree
    tree_data = []
    index = 1
    while True:
        # https://docs.gitlab.com/ee/api/index.html#pagination
        request_url = f'{gitlab_info.base_url}/repository/tree?recursive=yes&per_page=100&page={index}'
        print(request_url)
        headers = {
            'PRIVATE-TOKEN': gitlab_info.private_token
        }
        res, res_headers = req(request_url, headers)
        tree_data.extend(json.loads(res))
        if not res_headers.get('X-Next-Page') or res_headers.get('X-Total-Pages') == res_headers.get('X-Page'):
            break
        index += 1
    return tree_data


def get_repository_archive(gitlab_info: GitLabInfo) -> None:
    # https://docs.gitlab.com/ee/api/repositories.html#get-file-archive
    request_url = f'{gitlab_info.base_url}/repository/archive.zip'
    headers = {
        'PRIVATE-TOKEN': gitlab_info.private_token
    }
    res, _ = req(request_url, headers)
    archive_path = Path('data/repository/archive.zip')
    if not archive_path.parent.exists():
        archive_path.parent.mkdir(parents=True, exist_ok=True)
    with archive_path.open('wb') as f:
        f.write(res)

    with ZipFile(archive_path) as zf:
        zf.extractall(archive_path.with_name('archive'))


def set_actions(tree_data: list, target_path: Path, pattern: str, split_pattern: str) -> list:
    # https://docs.gitlab.com/ee/api/commits.html#create-a-commit-with-multiple-files-and-actions
    target_folder = Path(target_path)
    actions = list()


    exsisting_files = [p for item in tree_data if (p := item.get('path'))]

    # print(exsisting_files)
    for file in target_folder.glob(pattern):
        remote_file = Path(str(file)[:str(file).find(split_pattern)] + file.suffix)
        action_mode = 'create'
        if remote_file.as_posix() in exsisting_files:
            action_mode = 'update'

        with file.open('r') as f:
            content = f.read()
        action = {
            "action": action_mode,
            "file_path": remote_file.as_posix(),
            "content": content,
            "encoding": 'text'
        }
        print(f'{file.as_posix()}  ({action_mode})---> {remote_file.as_posix()}')
        actions.append(action)
    print('-------------')
    return actions


def commit(gitlab_info: GitLabInfo, tree_data: list, target_path: Path, pattern: str, split_pattern: str) -> dict:
    # https://docs.gitlab.com/ee/api/commits.html#create-a-commit-with-multiple-files-and-actions
    if not split_pattern:
        split_pattern = pattern
    post_url = f'{gitlab_info.base_url}/repository/commits'
    branch = 'main'
    commit_message = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    headers = {
        "method": "POST",
        "PRIVATE-TOKEN": gitlab_info.private_token,
        "Content-Type": "application/json"
    }

    actions = set_actions(tree_data, target_path, pattern, split_pattern)
    payload = {
        "branch": branch,
        "commit_message": commit_message,
        "actions": actions
    }

    while True:
        q=input('Do you want to commit? (yes/no)')
        if q=='yes':
            res, _ = req(post_url, headers=headers, data=json.dumps(payload).encode("utf-8"))
            commit_result = json.loads(res)
            # print(json.dumps(commit_result, indent=2))

            print('Commited at', commit_result.get('committed_date'))
            print('[Message]', commit_result.get('message'))
            print('[WebURL]', commit_result.get('web_url'))
            print('[Stats]')
            print('  Additions :', commit_result.get('stats').get('additions'))
            print('  Deletions :', commit_result.get('stats').get('deletions'))
            print('  Total     :', commit_result.get('stats').get('total'))
            print('Committed!')
            return commit_result
        elif q=='no':
            print('Not Committed')
            break


if __name__ == '__main__':
    gitlab_info = GitLabInfo()

    try:
        tree_data = get_tree_info(gitlab_info)
        get_repository_archive(gitlab_info)
        commit(gitlab_info, tree_data, 'data/commit_target', '*_last_*', '_last_')
    except urllib.error.HTTPError as err:
        print('Not Completed')
    except KeyboardInterrupt:
        print('\n\nKeyboard Interrupt!\n')
