import git

from commit import *
from const import *
from name_maps import *
from util import *

REPO = git.Repo(REPO_DIR)
NEW_REPO = git.Repo(NEW_REPO_DIR)
# BACKUP_REPO = git.Repo(REPO_BACKUP_BRANCH)

COMMIT_MAP = {}
ALL_APPLY_COMMITS = []

AUTHOR_SET = set()
EMAIL_SET = set()

AUTHOR_COMMIT_CNT = {}
AUTHOR_EMAIL_COMMIT_CNT = {}
NAME_EMAIL_MAP = {}

COMMIT_MSG_MAP = {}


def init_func(max_commit_cnt=-1):
    global ALL_APPLY_COMMITS
    global COMMIT_MAP
    global LAST_COMMIT

    checkout_branch(REPO, TMP_BRANCH, create_new=True)
    del_branch_local(REPO, REPO_BRANCH)
    checkout_branch(REPO, REPO_BACKUP_BRANCH)
    checkout_branch(REPO, REPO_BRANCH, create_new=True)

    LAST_COMMIT = REPO.head.commit.hexsha
    assert LAST_COMMIT, "LastCommit is empty"
    clean_repo(REPO)

    ALL_APPLY_COMMITS, COMMIT_MAP = collect_commits(REPO, REPO_BRANCH, count=max_commit_cnt)

    checkout_branch(NEW_REPO, NEW_REPO_BRANCH, create_new=True)
    reset_to_rev(NEW_REPO, INIT_COMMIT)
    clean_repo(NEW_REPO)

    reset_to_rev(REPO, INIT_COMMIT)
    clean_repo(REPO)


def process():
    print("Start process!\n")
    all_cnt = len(ALL_APPLY_COMMITS)
    in_map_cnt = 0
    in_map_abandon_cnt = 0
    not_in_map_abandon_cnt = 0

    for i, commit in enumerate(ALL_APPLY_COMMITS, 1):
        if commit.is_orphan:
            continue

        is_in_map = commit.commit_id in COMMIT_MSG_MAP
        in_map_cnt += 1 if is_in_map else 0
        if is_in_map:
            new_msg = COMMIT_MSG_MAP[commit.commit_id]
            commit.new_message = new_msg
            is_empty = new_msg == ""
            in_map_abandon_cnt += 1 if is_empty else 0
            if is_empty:
                continue
        else:
            if not commit.useful:
                not_in_map_abandon_cnt += 1
                continue

        copy_commit(REPO, NEW_REPO, commit)
        progress_bar_output(i, all_cnt)
    print('\n')
    print("Total cnt:%d\n" % all_cnt)
    print("Total in_map_cnt:%d\n" % in_map_cnt)
    print("Total abanon_in_map cnt:%d\n" % in_map_abandon_cnt)
    print("Total abanon_not_in_map cnt:%d\n" % not_in_map_abandon_cnt)
    apply_cnt = all_cnt - ( in_map_abandon_cnt + not_in_map_abandon_cnt)
    print("Total apply cnt:%d\n"%apply_cnt)
    print("\nProcess done!\n")


def copy_commit(repo, new_repo, commit):
    reset_to_commit(repo, commit)
    clean_repo(repo)
    files = list_files_in_commit(repo, commit)

    remove_all_tracked_files(new_repo, NEW_REPO_DIR, NEW_REPO_BRANCH)
    copy_files(files, REPO_DIR, NEW_REPO_DIR)
    apply_commit(new_repo, commit)


def collect_name_and_email(commits):
    for c in commits:
        name = c.author_name
        real_name = REPLICA_NAME_MAP.get(name, "")
        assert real_name
        email = c.author_email
        real_email = REPLICA_EMAIL_MAP.get(email, "")

        assert real_email, "%s not matched" % email

        NAME_EMAIL_MAP[real_name] = real_email
        AUTHOR_COMMIT_CNT[real_name] = AUTHOR_COMMIT_CNT.get(real_name, 0) + 1
        AUTHOR_EMAIL_COMMIT_CNT[real_email] = AUTHOR_EMAIL_COMMIT_CNT.get(real_email, 0) + 1

def save_commit_msg():
    save_commit_msg_by_author("/home/czs/author_msgs", ALL_APPLY_COMMITS, lambda c: True)

if __name__ == "__main__":
    init_func(-1)
    COMMIT_MSG_MAP = load_commit_message_map(COMMIT_FILE_DIR)

    if 1:
        ALL_APPLY_COMMITS[-1].is_mainline = True
        check_mainline(ALL_APPLY_COMMITS, COMMIT_MAP)
        collect_name_and_email(ALL_APPLY_COMMITS)
        MyCommit.NAME_EMAIL_MAP = NAME_EMAIL_MAP
        MyCommit.REPLICA_NAME_MAP = REPLICA_NAME_MAP
        simplify(ALL_APPLY_COMMITS, COMMIT_MAP)
        describe_commits(ALL_APPLY_COMMITS)
        process()