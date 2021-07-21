import sys
import glob
import os

from .excel import read_excel_file


def get_string_width(multi_string):
    lines = multi_string.split("\n")
    max_width = 0
    for l in lines:
        len_l = len(l)

        if max_width < len_l:
            max_width = len_l

    return max_width


def progress_bar_output(i, total):
    i = 100 * i // total

    sys.stdout.write('\r')
    sys.stdout.write("[%-100s] %d%%" % ('=' * i, i))
    sys.stdout.flush()


def load_commit_message_map(dir_path):
    """
    load all excel files and construct map of commit to new message
    :param dir_path: absolute director path which contain excel files
    :return: dict
    """
    ret = {}
    cnt_map = {}

    suffix = ".xlsx"
    all_paths = set(glob.glob("%s/*%s" % (dir_path, suffix)))
    total_cnt = 0
    for f in all_paths:
        df = read_excel_file(f)
        # df = df[~df['Keep'].isnull()]
        cnt = 0
        for _, row in df.iterrows():
            commitID = row['CommitUrl']
            assert isinstance(commitID, str)
            total_cnt += 1
            if row['Keep'] != 1:
                ret[commitID] = ""
                continue

            cnt += 1
            msg = row['Message'].strip()
            assert commitID not in ret
            ret[commitID] = msg
        name = os.path.basename(f[0:-len(suffix)])
        cnt_map[name] = cnt

    # for x, y in ret.items():
    #     print(x, " ", y + "\n")
    # print(ret)
    print("In load commit msg start:\n")
    print("==================\n")
    for name, cnt in cnt_map.items():
        print("\t%s:%d\n" % (name, cnt))
    print("total cnt:", total_cnt)
    print("keep1 cnt:", sum(cnt_map.values()))

    print("==================\n")
    print("In load commit msg end.\n")
    return ret

# def add_time_to_datetime(t, duration):
#     from datetime import datetime, timedelta
#     x = datetime.now() + timedelta(seconds=3)
#     x += timedelta(seconds=18)
