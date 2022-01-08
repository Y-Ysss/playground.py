
import time
import datetime
import urllib.request
import urllib.parse
import json
import pprint
import re
import base64

# gitで管理するethercalcコンテンツのURL
ethercalc_uris = [ "http://localhost/foo", "http://localhost/bar" ]

# GitLab関連
gitlab_base_uri = "http://localhost:10080/"

# gitリポジトリ内でのバックアップ先
gitlab_backup_directory = "ethercalc"

gitlab_private_token = "6f8YXyrZ1SCSADHTJ2L9"
gitlab_project_id = 3

# 今
str_now = datetime.datetime.today().strftime("%Y%m%d_%H%M%S")

# 改行
LF = '\n'


def get_gitlab_file(private_token, file_path):
    """
    GitLabリポジトリから1ファイルを取得する

    Parameters
    ----------
    private_token : str
        GitLab API用アクセストークン

    file_path : str
        gitリポジトリのトップからのファイルパス

    Returns
    -------
    anonymous : json
        GitLabからのレスポンス
    """

    # https://docs.gitlab.com/ee/api/repository_files.html
    gitlab_uri = f"{gitlab_base_uri}api/v4/projects/{gitlab_project_id}/repository/files/{urllib.parse.quote(file_path, safe='')}?ref=master"
    logger.info(f"gitlab_uri={gitlab_uri}")
    headers = {
        "PRIVATE-TOKEN": private_token
    }
    request = urllib.request.Request(gitlab_uri, headers=headers)
    try:
        with urllib.request.urlopen(request) as res:
            res_files = json.loads(res.read())
    except urllib.error.HTTPError as ee:
        if ee.code == 404:
            return {}
        else:
            raise
    except:
        raise
    else:
        # logger.debug(f"gitlab res_commit={LF}{pprint.pformat(res_files)}")
        return res_files


def compare_ethercalc_and_gitlab(actions, ethercalc_uri, git_filename):
    """
    EtherCalcとGitLabリポジトリからファイルを取得して比較し、差異があればactions変数にactionを追加する

    Parameters
    ----------
    actions : list
        後に GitLabの commits APIに渡す actions変数

    ethercalc_uri : str
        EtherCalcのURI

    git_filename : str
        gitリポジトリでのファイル名

    Returns
    -------
    なし
    """

    logger.info(f"ethercalc URL={ethercalc_uri}")

    # EtherCalcからダウンロード
    request = urllib.request.Request(ethercalc_uri)
    with urllib.request.urlopen(request) as res:
        content_ethercalc = res.read().decode("utf-8")
    # logger.debug(f"content_ethercalc={LF}{content_ethercalc}")

    # GitLabからダウンロード
    action_str = ""
    file_path = f"{gitlab_backup_directory}/{git_filename}"
    res_gitlab_file = get_gitlab_file(gitlab_private_token, file_path)
    try:
        content_gitlab = base64.b64decode(res_gitlab_file["content"]).decode("utf-8")
    except KeyError:
        # GitLabにファイルがない時は、後に新規作成してgit commit＆push
        action_str = "create"
    except:
        raise
    else:
        # logger.debug(f"content_gitlab={LF}{content_gitlab}")

        # EtherCalcとGitLabからダウンロードしたファイルを比較
        if content_ethercalc == content_gitlab:
            logger.info("content_ethercalc == content_gitlab")
        else:
            logger.info("content_ethercalc != content_gitlab")
            # ファイル内容に差異がある時、後にgit commit＆push
            action_str = "update"

    # actionがcreateまたはupdateの時、actions変数に登録
    if 0 < len(action_str):
        action = {
            "action": action_str,
            "file_path": file_path,
            "content": content_ethercalc
        }
        actions.append(action)


def main():
    # ethercalc_urisの各URLを処理
    actions = list()
    count_commit = 0
    re_compile = re.compile(r".*/(.*?)$")
    for index, ethercalc_uri in enumerate(ethercalc_uris):
        basename, = re_compile.match(ethercalc_uri).groups()    # 文字列 "foo"、"bar" を取り出す
        socialcalc_uri = ethercalc_uri[::-1].replace(basename[::-1], basename[::-1] + "/_", 1)[::-1]
        csv_uri = ethercalc_uri + ".csv"
        logger.info(f"[{index}] {basename}")

        # SocialCalc形式でEtherCalcとGitLabからダウンロードして、ファイル内容比較
        time.sleep(0.5)     # DoS攻撃にならないように適当にsleep
        compare_ethercalc_and_gitlab(actions, socialcalc_uri, f"{basename}.sc")

        # csv形式でEtherCalcとGitLabからダウンロードして、ファイル内容比較
        time.sleep(0.5)     # DoS攻撃にならないように適当にsleep
        compare_ethercalc_and_gitlab(actions, csv_uri, f"{basename}.csv")

        if len(actions) == 0:
            # EtherCalcとGitLabのファイル内容に差異がなければ git commitしない
            continue

        # git commit ＆ push
        # https://docs.gitlab.com/ee/api/commits.html
        gitlab_uri = f"{gitlab_base_uri}api/v4/projects/{gitlab_project_id}/repository/commits"
        commit_message = datetime.datetime.today().strftime(f"backup {str_now} {basename}")
        logger.info(f'git commit -m "{commit_message}"')
        headers = {
            "method": "POST",
            "PRIVATE-TOKEN": gitlab_private_token,
            "Content-Type": "application/json"
        }
        payload = {
            "branch": "master",
            "commit_message": commit_message,
            "actions": actions
        }
        logger.debug(f"payload={LF}{pprint.pformat(payload)}")

        request = urllib.request.Request(gitlab_uri, json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(request) as res:
            res_commit = json.loads(res.read())
        logger.debug(f"gitlab res_commit={LF}{pprint.pformat(res_commit)}")

        # git diff してログに出力
        # https://docs.gitlab.com/ee/api/commits.html
        gitlab_uri = f"{gitlab_base_uri}api/v4/projects/{gitlab_project_id}/repository/commits/{res_commit['id']}/diff"
        logger.info(f"git diff ( {res_commit['id']} )")
        headers = {
            "PRIVATE-TOKEN": gitlab_private_token,
        }
        request = urllib.request.Request(gitlab_uri, headers=headers)
        with urllib.request.urlopen(request) as res:
            res_diff = json.loads(res.read())
        logger.info(f"gitlab res_diff={LF}{pprint.pformat(res_diff)}")

        count_commit += 1
        actions = list()

    logger.info(f"{count_commit} 件 git commit しました")


if __name__ == '__main__':
    try:
        main()
    except Exception as ee:
        logger.exception(ee)