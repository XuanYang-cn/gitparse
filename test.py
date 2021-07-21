from parser.util import load_commit_message_map


MY_COMMIT_FILE_PATH = "/home/yangxuan/Github/gitparse/commit_files/"


def test_load_commit_message_map():
    load_commit_message_map(MY_COMMIT_FILE_PATH)


if __name__ == '__main__':
    test_load_commit_message_map()
