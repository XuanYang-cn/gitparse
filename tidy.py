import git
import csv
import time
import re


commit_summary = """
---------------------------
Number ({}):
 - Author: {},
 - Author email: {}
 - Authored date: {},
 - Committer: {},
 - Committer email: {},
 - Committed date: {},
 - Message summary: {}
 - Message: {}
"""


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
        self.commits = [(c.author.name,
                         c.author.email,
                         c.authored_date,
                         c.committer.name,
                         c.committer.email,
                         c.committed_date,
                         c.summary,
                         c.message
                         ) for c in self.repo.iter_commits(branch, paths)]

        self.commits.reverse()

        for c in self.repo.iter_commits(branch, paths):
            if c.author.name not in self._authors:
                if "zilliz.com" in c.author.email:
                    self._authors[c.author.name] = c.author.email
                else:
                    self._authors[c.author.name] = self.get_email_from_signed_off(c.message)

        if write_csv:
            with open(self.csvfile, 'w', newline='') as csvfile:
                commitwriter = csv.writer(csvfile)
                commitwriter.writerows(self.commits)

    def get_email_from_signed_off(self, message: str) -> str:
        pattern = re.compile(r"\<.*\>")
        return pattern.findall(message)[-1][1:][:-1]

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


def test_authors(repo: TargetRepo):
    print("== Test Authors ==")
    repo.init_commits("main", False, ["pymilvus_orm", "tests", "docs"])

    from pprint import pprint
    pprint(repo.authors)


if __name__ == "__main__":
    REPO = "/home/yangxuan/Github/pymilvus-orm"
    pymilvus_orm = TargetRepo(REPO)

    #  pymilvus_orm.init_commits("main", True, ["pymilvus_orm", "tests", "docs"])
    #  print(pymilvus_orm)
    #  pymilvus_orm.read_commits()
    #  print(pymilvus_orm)

    test_authors(pymilvus_orm)
