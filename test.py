import git

from parser.util import load_commit_message_map
from parser.excel import create_table_for_author

from parser.commit import save_commit_msg_by_author, collect_commits


MY_COMMIT_FILE_PATH = "/home/yangxuan/Github/gitparse/commit_files/"
REPO = "/home/yangxuan/Github/pymilvus-orm"


def test_load_commit_message_map():
    load_commit_message_map(MY_COMMIT_FILE_PATH)


def test_collect_commits():
    repo = git.Repo(REPO)
    commits, maps = collect_commits(repo, "main")


if __name__ == '__main__':
    test_collect_commits()
