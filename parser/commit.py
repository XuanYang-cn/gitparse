import os
import shutil
from datetime import timedelta

from .const import REPO_DIR, NEW_REPO_DIR
from .excel import create_table_for_author


class MyCommit:
    REPLICA_NAME_MAP = {}
    NAME_EMAIL_MAP = {}
    # START_DATETIME = datetime.now()
    START_DATETIME = None
    START_COMMIT = None

    def __init__(self, commit, order):
        self._commit = commit
        self._solved = False
        self._is_mainline = False
        self._order = order
        self.mainline_checked = False
        self.useful = True
        self._new_msg = None

    def judge_by_child(self, child_commit):

        if self._is_mainline:
            return

        if self.real_author_name == child_commit.real_author_name:
            self.useful = False

        self._solved = self._solved or child_commit.left_parent_id == self.commit_id or child_commit.right_parent_id == self.commit_id

    @property
    def is_orphan(self):
        return self.left_parent_id is None and self.right_parent_id is None

    @property
    def is_mainline(self):
        return self._is_mainline

    @is_mainline.setter
    def is_mainline(self, mainline):
        self._is_mainline = mainline
        self.mainline_checked = True

    def has_single_parent(self):
        return len(self._commit.parents) <= 1

    @property
    def left_parent_id(self):
        if not self._commit.parents:
            return
        return self._commit.parents[0].hexsha

    @property
    def right_parent_id(self):
        if not self.has_single_parent():
            return self._commit.parents[1].hexsha
        return None

    @property
    def solved(self):
        return self.is_mainline or self._solved

    @solved.setter
    def solved(self, solved):
        self._solved = solved

    @property
    def commit_id(self):
        return self._commit.hexsha

    @property
    def order(self):
        return self._order

    @order.setter
    def order(self, order):
        self._order = order

    @property
    def authored_date(self):
        return self._commit.authored_date

    @property
    def authored_datetime(self):
        return self._commit.authored_datetime

    @property
    def author_name(self):
        return self._commit.author.name

    @property
    def real_author_name(self):
        return self.REPLICA_NAME_MAP.get(self.author_name, "")

    @property
    def author_email(self):
        return self._commit.author.email

    @property
    def real_author_email(self):
        return self.NAME_EMAIL_MAP.get(self.real_author_name, "")

    @property
    def committer_name(self):
        return self._commit.committer.name

    @property
    def real_committer_name(self):
        return self.REPLICA_NAME_MAP.get(self.committer_name, "")

    @property
    def committer_email(self):
        return self._commit.committer.email

    @property
    def real_committer_email(self):
        return self.NAME_EMAIL_MAP.get(self.real_committer_name, "")

    @property
    def message(self):
        return self._commit.message

    @property
    def new_message(self):
        if self._new_msg is None:
            return self.message
        return self._new_msg

    @new_message.setter
    def new_message(self, msg):
        self._new_msg = msg

    @property
    def summary(self):
        return self._commit.summary

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.order < other.order
        return self.order < other

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.order == other.order
        return self.order == other

    def __str__(self):
        return self._commit_id


def set_user_and_email(repo, user, email):
    repo.config_writer().set_value("user", "name", user).release()
    repo.config_writer().set_value("user", "email", email).release()


def reset_to_rev(repo, rev):
    repo.git.execute(
        ['git', 'reset', '--hard', rev])


def clean_repo(repo):
    repo.git.clean('-xdf')


def reset_to_commit(repo, commit):
    reset_to_rev(repo, commit.commit_id)


def del_branch_local(repo, branch):
    try:
        repo.git.execute(
            ['git', 'branch', '--d', branch])
    except Exception:
        pass


def list_files_in_commit(repo, commit):
    files = repo.git.execute(
        ['git', 'ls-tree', '--name-only', commit.commit_id]).split()
    return files


def fixup_faiss_link(repo_dir):
    rel_dirs = [
        "internal/core/src/index/thirdparty/faiss",
        "core/src/index/thirdparty/faiss",
    ]
    for r_dir in rel_dirs:
        _fixup_faiss_link(repo_dir, r_dir)


def _fixup_faiss_link(repo_dir, relative_dir):
    target_dir = "%s/%s" % (repo_dir, relative_dir)
    faiss_link_dir = "%s/faiss" % target_dir
    if not os.path.exists(faiss_link_dir):
        return
    if not os.path.islink(faiss_link_dir):
        return

    wd = os.getcwd()
    os.chdir(target_dir)
    os.remove(faiss_link_dir)
    os.symlink(".", 'faiss')
    os.chdir(wd)


def fixup_missing_file(repo, repo_dir):
    fname = ".gitignore"
    new_lines = []
    old_lines = []
    with open("%s/%s" % (repo_dir, fname), "r") as f:
        old_lines.extend(f.readlines())
        new_lines.extend([line for line in old_lines if line != 'lib/\n'])

    with open("%s/%s" % (repo_dir, fname), "w") as f:
        f.writelines(new_lines)

    repo.git.add(".")

    with open("%s/%s" % (repo_dir, fname), "w") as f:
        f.writelines(old_lines)


def replace_msg(commit_id, msg):
    # mainly to remove pr number
    replace_map = {
        '65fd57fdceaac6391e53328b72fd0ce13c18ca4d': 'Add docker-compose yaml for distributed and standalone',
        '2d5eed2dd96be4955e74c2677cf0326472f28cfe': 'Support segcoreinit',
        '7d97b816876a090ec3d7a4ee3380d1840ad2e05c': 'Make query node asynchronously load and release collection',
        'b4651f1ccae4a46e2c14ba5064e734beaee8a6d0': 'Add unit tests in dataservice',
        '5bbe916ccae2d9597e6806ae8d652efb5423f619': 'Fix collection cannot be found when searching',
        '5993b6cf1eab6fb47832bd18155f552ae52795c0': 'Add unittest for storage',
    }
    return replace_map.get(commit_id, msg)


def add_singed_off(msg, author, email):
    # Signed-off-by: yudong.cai <yudong.cai@zilliz.com>
    prefix = "Signed-off-by:"
    if prefix in msg:
        return msg
    sign_msg = " ".join([prefix, author, "<%s>" % email])
    msg = msg + "\n\n" + sign_msg
    return msg


def apply_commit(repo, src_commit):
    author_name = src_commit.real_author_name
    author_email = src_commit.real_author_email
    # author_date_str = src_commit.authored_datetime.strftime('%Y-%m-%d %H:%M:%S')
    d_datetime = src_commit.authored_datetime - timedelta(hours=8)
    author_date_str = d_datetime.strftime('%Y-%m-%d %H:%M:%S %z')

    os.environ["GIT_AUTHOR_DATE"] = author_date_str
    os.environ["GIT_COMMITTER_DATE"] = author_date_str
    set_user_and_email(repo, author_name, author_email)

    target_id = '1bbe40ef7ca3b56850142af581d94f5668815a8b'
    if src_commit.commit_id == target_id:
        fixup_missing_file(repo, NEW_REPO_DIR)

    fixup_faiss_link(NEW_REPO_DIR)

    repo.git.add(".")
    msg = replace_msg(src_commit.commit_id, src_commit.new_message)
    msg = msg.strip()
    msg = add_singed_off(msg, author_name, author_email)
    repo.index.commit(msg)


def apply_commit2(repo, src_commit):

    MyCommit.START_DATETIME = MyCommit.START_DATETIME + timedelta(seconds=18)
    d_datetime = MyCommit.START_DATETIME - timedelta(hours=8)
    author_name = src_commit.real_author_name
    author_email = src_commit.real_author_email

    # author_date_str = src_commit.authored_datetime.strftime('%Y-%m-%d %H:%M:%S')
    # date2 = src_commit.authored_datetime
    # timestamp = MyCommit.START_DATETIME.time
    author_date_str = d_datetime.strftime('%Y-%m-%d %H:%M:%S %z')

    os.environ["GIT_AUTHOR_DATE"] = author_date_str
    os.environ["GIT_COMMITTER_DATE"] = author_date_str
    set_user_and_email(repo, author_name, author_email)

    target_id = '1bbe40ef7ca3b56850142af581d94f5668815a8b'
    if src_commit.commit_id == target_id:
        fixup_missing_file(repo, NEW_REPO_DIR)

    fixup_faiss_link(NEW_REPO_DIR)

    repo.git.add(".")
    msg = src_commit.new_message
    repo.index.commit(msg)


def checkout_branch(repo, branch, create_new=False):
    does_exist = True
    try:
        repo.git.checkout(branch)
    except Exception:
        does_exist = False

    if not does_exist:
        if not create_new:
            raise Exception('{branch} not existed'.format(branch=repr(branch)))
        else:
            repo.git.checkout('-b', branch)


def merge_branch(repo, branch):
    repo.git.execute(
        ['git', 'merge', branch])


def describe_commits(commits):
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0  # solved
    cnt4 = 0  # useful

    notuseful_map = {}
    useful_map = {}
    for c in commits:
        assert c.mainline_checked
        if c.is_mainline:
            cnt1 += 1
        else:
            cnt2 += 1

        if c.solved:
            cnt3 += 1

        if c.useful:
            cnt4 += 1
            useful_map[c.real_author_name] = useful_map.get(c.real_author_name, 0) + 1
        else:
            notuseful_map[c.real_author_name] = notuseful_map.get(c.real_author_name, 0) + 1

        if c.is_mainline:
            pass

    print("mainline cnt:", cnt1)
    print("subline cnt:", cnt2)
    print("solved cnt:", cnt3)
    print("useful cnt:", cnt4)

    if 0:
        print("Useful:")
        for x, y in useful_map.items():
            print("%s:%d" % (x, y))

        print("Not Useful")
        for x, y in notuseful_map.items():
            print("%s:%d" % (x, y))


dir_link_map = {}


def copy_dir(src, dst):
    # src : /home/czs/xxx
    # src_name  xxx
    # dst : /home/czs/dummy
    src_name = os.path.basename(src)
    target_dir = os.path.join(dst, src_name)

    if os.path.islink(src):
        # if os.path.isdir(src): return
        os.symlink(src, target_dir)
        dir_link_map[src] = target_dir
        return

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    # mkdir /home/czs/dummy/xxx

    files = os.listdir(src)
    for eachfile in files:
        fn = os.path.join(src, eachfile)
        islink = os.path.islink(fn)
        isdir = os.path.isdir(fn)
        if isdir:
            copy_dir(fn, target_dir)
        else:
            shutil.copy(fn, target_dir, follow_symlinks=islink)


def collect_commits(repo, branch, count=-1):
    my_commits = []
    commit_map = {}
    commits = list(repo.iter_commits(branch))
    commits.reverse()
    if count > 0:
        commits = commits[:count]
    else:
        commits = commits[:]

    print(commits)
    for i, c in enumerate(commits):
        my_c = MyCommit(c, i)
        my_commits.append(my_c)
        commit_map[my_c.commit_id] = my_c

    return my_commits, commit_map


def remove_all_files(directory):
    if not directory:
        return

    if not os.path.isdir(directory):
        return

    if not os.path.exists(directory):
        return

    if os.path.islink(directory):
        os.unlink(directory)

    c = os.path.realpath(directory) + os.sep
    p1 = os.path.realpath(REPO_DIR) + os.sep
    issub1 = c.startswith(p1)
    p2 = os.path.realpath(NEW_REPO_DIR) + os.sep
    issub2 = c.startswith(p2)
    if not issub1 and not issub2:
        return

    cmd = "rm -fr %s/*" % directory
    os.system(cmd)


def remove_all_tracked_files(repo, repo_dir, branch):
    files = repo.git.execute(
        ['git', 'ls-tree', '--name-only', branch]).split()

    ret = [os.path.join(repo_dir, f) for f in files]
    for f in ret:
        if os.path.isdir(f):
            shutil.rmtree(f)
        elif os.path.islink(f):
            os.unlink(f)
        elif os.path.isfile(f):
            os.remove(f)


def check_mainline(commits, commit_map):
    old_cnt = 1
    cnt = 0
    while (old_cnt != cnt):
        old_cnt = cnt
        for c in reversed(commits):
            if c.mainline_checked:
                left_parent_id = c.left_parent_id
                lp = commit_map.get(left_parent_id, None)
                if lp and c.is_mainline:
                    lp.is_mainline = True

        cnt = 0
        for c in commits:
            if c.mainline_checked:
                cnt += 1

    for c in commits:
        if not c.mainline_checked:
            c.is_mainline = False


def simplify(commits, commit_map):
    for c in reversed(commits):
        left_parent_id = c.left_parent_id
        lp = commit_map.get(left_parent_id, None)
        if lp:
            lp.judge_by_child(c)

        right_parent_id = c.right_parent_id
        rp = commit_map.get(right_parent_id, None)
        if rp:
            rp.judge_by_child(c)


link_file_map = set()


def copy_files(files, srcDir, dstDir):
    for file in files:
        if os.path.islink(file):
            link_file_map.add(file)
        # continue
        file_path = os.path.join(srcDir, file)
        if os.path.isfile(file_path):
            shutil.copy(file_path, dstDir, follow_symlinks=True)
        elif os.path.isdir(file_path):
            copy_dir(file_path, dstDir)


def save_commit_msg_by_author(target_dir, commits, checkFunc):
    author_msgs = {}
    titles = ["Date", "CommitUrl", "Keep", "Message"]
    widths = [0, 0, 0]

    for c in commits:
        if checkFunc(c):
            real_author_name = c.real_author_name
            author_date_str = c.authored_datetime.strftime('%Y-%m-%d %H:%M:%S')
            url = "https://github.com/zilliztech/milvus-distributed/commit/" + c.commit_id
            hyperlink = '=HYPERLINK(\"%s\", \"%s\")' % (url, c.commit_id)
            keep = 1 if c.useful else None
            values = [author_date_str, hyperlink, keep, c.message]

            widths[0] = len(author_date_str)
            widths[1] = len(c.commit_id)
            widths[2] = 6

            if real_author_name not in author_msgs:
                author_msgs[real_author_name] = {key: [] for key in titles}

            for i, key in enumerate(titles):
                author_msgs[real_author_name][key].append(values[i])

    for author, content in author_msgs.items():
        fname = "%s/%s" % (target_dir, repr(author))
        create_table_for_author(fname, content, widths)


def save_mainline_msg(target_dir, commits):
    save_commit_msg_by_author(target_dir, commits, lambda c: c.is_mainline)


def save_useful_msg(target_dir, commits):
    save_commit_msg_by_author(target_dir, commits, lambda c: c.useful)


if __name__ == '__main__':
    fixup_faiss_link('/home/czs/dmilvus2')
