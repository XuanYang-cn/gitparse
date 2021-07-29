from tidy import (
    BaseRepo,
    TargetRepo,
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
