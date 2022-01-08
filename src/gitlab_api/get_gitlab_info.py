import configparser
from dataclasses import dataclass
from pathlib import Path

info_data = """
[gitlab]
url=
project_id=
private_token=
"""


@dataclass
class GitLabInfo():
    internal_gitlab_url: str
    project_id: int
    private_token: str
    base_url: str

    def __init__(self) -> None:
        info_file_path = Path(__file__).with_name('gitlab_info.ini')

        if not info_file_path.exists():
            with info_file_path.open('w') as f:
                f.write(info_data)

        _conf_parser = configparser.ConfigParser()
        _conf_parser.read(info_file_path)
        self.internal_gitlab_url = _conf_parser.get('gitlab', 'url')
        self.project_id = _conf_parser.get('gitlab', 'project_id')
        self.private_token = _conf_parser.get('gitlab', 'private_token')
        self.base_url = f'{self.internal_gitlab_url}/api/v4/projects/{self.project_id}'


if __name__ == '__main__':
    conf = GitLabInfo()
    print(conf.internal_gitlab_url)
    print(conf.project_id)
    print(conf.private_token)
