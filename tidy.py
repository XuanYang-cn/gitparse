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

    def rebase(self):
        self.repo.git.execute(['git', 'rebase', '--committer-date-is-author-date', 'upstream/master'])


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
        # Progress printing
        num = int(i / target_num * 100)
        s = "#" * num
        o = "-" * (100 - num)
        print(f"{s}{o} |{(i / target_num) * 100:.2f}%")

        pymilvus_orm.reset2rev(commit[0])
        pymilvus_orm.repo.git.execute(['git', "clean", "-fd"])
        copy(pymilvus_orm.path, os.path.join(pymilvus.path, "orm"))

        pymilvus.commit(*commit[1:])

    print("Rebasing")
    pymilvus.rebase()


def copy(src, dst):
    #  print(f"src: {src}\ndst: {dst}")
    files = ["pymilvus_orm", "milvus_orm", "tests", "docs"]
    #  print(f"Removing files in {dst} {os.listdir(dst)}")
    [shutil.rmtree(os.path.join(dst, d)) for d in os.listdir(dst)]

    [shutil.copytree(os.path.join(src, s), os.path.join(dst, s)) for s in files if os.path.isdir(os.path.join(src, s))]


if __name__ == "__main__":
    excute()
