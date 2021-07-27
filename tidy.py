import git
import csv
import time


commit_summary = """---------------------------
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
        self.author2email = {}
        self._commits = []

    def init_commits(self, branch: str, paths=None):
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

        with open(self.csvfile, 'w', newline='') as csvfile:
            commitwriter = csv.writer(csvfile)
            commitwriter.writerows(self.commits)

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


if __name__ == "__main__":
    REPO = "/home/yangxuan/Github/pymilvus-orm"
    pymilvus_orm = TargetRepo(REPO)

    #  pymilvus_orm.init_commits("main", ["pymilvus_orm", "tests", "docs"])
    #  print(pymilvus_orm)
    pymilvus_orm.read_commits()
    print(pymilvus_orm)
