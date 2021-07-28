import git
import csv
import time
import re


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


def test__init_commits(repo: BaseRepo):
    print(repo)


class TargetRepo:
    def __init__(self, path: str, csvfile=None):
        self.csvfile = 'eggs.csv' if not csvfile and not isinstance(csvfile, str) else csvfile
        self.repo = git.Repo(path)
        self.commits = []
        self._authors = {}
        self.author2email = {}
        self._commits = []
        self.toreplace = {"Wang Xiangyu": "Xiangyu Wang"}

    def init_commits(self, branch: str, write_csv=False, paths=None):
        #  time.asctime(time.localtime(c.authored_date)

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

    test__init_commits(pymilvus)


if __name__ == "__main__":
    test_BaseRepo()
