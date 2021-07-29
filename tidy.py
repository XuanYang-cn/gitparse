import git
import csv
import re
import os
import shutil
from datetime import datetime


commit_summary = """
---------------------------
Number ({}):
 - HexSha: {},
 - Author: {},
 - Author email: {}
 - Authored date: {},
 - Committer: {},
 - Committer email: {},
 - Committed date: {},
 - Message summary: {}
 - Message: {}
"""

commit_summary_brief = """
---------------------------
Number ({}):
 - HexSha: {},
 - Author: {},
 - Authored date: {},
 - Message summary: {}
"""

# PyMilvus commit at 2021-04-13
TARGET_COMMIT_ID = "56ad18acc259221b8e965c380261730114777ba2"


class BaseRepo:

    def __init__(self, path: str, new_branch="new_branch"):
        self.repo = git.Repo(path)
        self.path = self.repo.working_tree_dir
        try:
            self.repo.git.checkout("upstream/master")
            self.repo.git.execute(['git', 'branch', '-D', new_branch])
        except Exception:
            pass
        finally:
            self.repo.git.checkout(TARGET_COMMIT_ID, '-b', new_branch)
        self.__init_commits(new_branch)

    def __init_commits(self, branch: str):
        self.commits = [[c.hexsha,
                         c.author.name,
                         c.authored_date,
                         c.summary,
                         ] for c in self.repo.iter_commits(branch)]
        self.commits.reverse()

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        res = ""
        for i, c in enumerate(self.commits, 1):
            res += commit_summary_brief.format(i, *c)

        return res

    def commit(self,
               author: str, author_email: str, authored_date: int,
               committer: str, committer_email: str, committed_date: int,
               summary: str, commit_message: str):

        self.repo.git.add(os.path.join(self.path, "orm"))

        self.repo.index.commit(
            commit_message,
            author=git.Actor(author, author_email),
            committer=git.Actor(committer, committer_email),
            author_date=str(datetime.fromtimestamp(authored_date)),
            commit_date=str(datetime.fromtimestamp(committed_date)),
        )


def test__init_commits(repo: BaseRepo):
    print(repo)


def test_commit(repo: BaseRepo):
    kw = {
        "author": "zhenshan.cao",
        "author_email": "zhenshan.cao@zilliz.com",
        "authored_date": 1618372076,
        "committer": "GitHub",
        "committer_email": "noreply@github.com",
        "committed_date": 1618372076,
        "commit_message": "Establish the initial directory structure and copy the document files",
    }

    #  paths = ["pymilvus_orm", "tests", "docs"]
    repo.commit(**kw)
    pass


class TargetRepo:
    def __init__(self, path: str, csvfile=None):
        self.csvfile = 'eggs.csv' if not csvfile and not isinstance(csvfile, str) else csvfile
        self.repo = git.Repo(path)
        self.path = self.repo.working_tree_dir
        self.commits = []
        self._authors = {}
        self.author2email = {}
        self._commits = []

    def init_commits(self, branch: str, write_csv=False, paths=None):

        for i, c in enumerate(self.repo.iter_commits(branch, paths)):
            if c.author.name not in self._authors:
                if "zilliz.com" in c.author.email:
                    self._authors[c.author.name] = c.author.email
                else:
                    signed_off_email = self.get_email_from_signed_off(c.message)
                    self._authors[c.author.name] = signed_off_email if signed_off_email else c.author.email

        self.commits = [[c.hexsha,
                         c.author.name,
                         self._authors[c.author.name],
                         c.authored_date,
                         c.committer.name,
                         c.committer.email,
                         c.committed_date,
                         self.remove_pr_number_in_message(c.summary),
                         self.remove_pr_number_in_message(c.message)
                         ] for c in self.repo.iter_commits(branch, paths)]

        self.commits.reverse()
        if write_csv:
            with open(self.csvfile, 'w', newline='') as csvfile:
                commitwriter = csv.writer(csvfile)
                commitwriter.writerows(self.commits)

    def get_email_from_signed_off(self, message: str) -> str:
        # pattern for <aaa@bbb.com>
        pattern = re.compile(r"\<(.*)\>")
        b = pattern.search(message)
        return b.group(1) if b else ""

    def remove_pr_number_in_message(self, message: str) -> str:
        # pattern for (#123)
        pattern = re.compile(r"\(#\d+\)")
        b = pattern.search(message)
        if b:
            return message.replace(b.group(), "")
        return message

    def reset2rev(self, rev):
        self.repo.git.execute(['git', 'reset', '--hard', rev])

    def recover(self, rev="upstream/main"):
        self.repo.git.execute(['git', 'reset', '--hard', rev])

    @property
    def authors(self):
        return self._authors

    def read_commits(self):
        with open(self.csvfile, newline='') as csvfile:
            commitreader = csv.reader(csvfile)
            self._commits = [tuple(row) for row in commitreader]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        res = ""
        if self.commits:
            for i, c in enumerate(self.commits, 1):
                res += commit_summary.format(i, *c)
        else:
            for i, c in enumerate(self._commits, 1):
                res += commit_summary.format(i, *c)

        return res


def test_authors(repo: TargetRepo, branch, paths=None, test=False):
    print("== Test Authors ==")
    repo.init_commits(branch, False, paths)

    if test:
        from pprint import pprint
        pprint(repo.authors)


def test_commit_message(repo: TargetRepo, branch, paths=None, test=False):
    print("== Test Commit Messages ==")
    repo.init_commits(branch, False, paths)

    if test:
        print(repo)


def test_TargetRepo():
    ORM_REPO = "/home/yangxuan/Github/pymilvus-orm"
    pymilvus_orm = TargetRepo(ORM_REPO)

    #  pymilvus_orm.init_commits("main", True, ["pymilvus_orm", "tests", "docs"])
    #  print(pymilvus_orm)
    #  pymilvus_orm.read_commits()
    #  print(pymilvus_orm)

    test_authors(pymilvus_orm, "main", ["pymilvus_orm", "tests", "docs"])
    test_commit_message(pymilvus_orm, "main", ["pymilvus_orm", "tests", "docs"])


def test_BaseRepo():
    PYMILVUS_REPO = "/home/yangxuan/Github/pymilvus"
    pymilvus = BaseRepo(PYMILVUS_REPO)

    #  test__init_commits(pymilvus)
    test_commit(pymilvus)


def excute():
    ORM_REPO = "/home/yangxuan/Github/pymilvus-orm"
    pymilvus_orm = TargetRepo(ORM_REPO)

    PYMILVUS_REPO = "/home/yangxuan/Github/pymilvus"
    pymilvus = BaseRepo(PYMILVUS_REPO)

    pymilvus_orm.init_commits("upstream/main", True, ["pymilvus_orm", "tests", "docs"])
    base_dir = os.path.join(pymilvus.path, "orm")
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)

    target_num = len(pymilvus_orm.commits)
    for i, commit in enumerate(pymilvus_orm.commits, 1):
        num = int(i / target_num * 100)
        s = "#" * num
        o = "-" * (100 - num)
        print(f"{s}{o} |{(i / target_num) * 100:.2f}%")

        pymilvus_orm.reset2rev(commit[0])

        pymilvus_orm.repo.git.execute(['git', "clean", "-fd"])
        copy(pymilvus_orm.path, os.path.join(pymilvus.path, "orm"))

        pymilvus.commit(*commit[1:])


def copy(src, dst):
    #  print(f"src: {src}\ndst: {dst}")
    files = ["pymilvus_orm", "milvus_orm", "tests", "docs"]
    srcs = (os.path.join(src, f) for f in files)
    #  print(f"Removing files in {dst} {os.listdir(dst)}")
    [shutil.rmtree(os.path.join(dst, d)) for d in os.listdir(dst)]

    src_files = []

    def iter_files(src):
        for root, dirs, files in os.walk(src):
            root_d = root.replace("-", "/")
            if not os.path.isdir(root_d):
                #  print(f"Making directory {root_d}")
                os.mkdir(root_d)

            src_files.extend([os.path.join(root, f) for f in files])
            for d in dirs:
                current_d = os.path.join(root_d, d)
                if not os.path.isdir(current_d):
                    #  print(f"Making directory {current_d}")
                    os.mkdir(current_d)

    list(map(iter_files, srcs))

    def copy(source):
        pass
        #  print(f"Copy from {source} to {source.replace('-', '/')}")
        shutil.copy(source, source.replace("-", "/"))

    #  print(f"Copying files total: {len(src_files)}")
    list(map(copy, src_files))


if __name__ == "__main__":
    excute()
