import sys
import glob
import os

from excel import read_excel_file

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
    all_paths = set(glob.glob("%s/*%s"%(dir_path, suffix)))
    total_cnt = 0
    total_cnt2 = 0
    for f in all_paths:
        df = read_excel_file(f)
        # df = df[~df['Keep'].isnull()]
        cnt = 0
        for _, row in df.iterrows():
            commitID = row['CommitUrl']
            assert isinstance(commitID, str)

            if row['Keep'] != 1:
                ret[commitID] = ""
                total_cnt2 += 1
                continue

            cnt += 1
            total_cnt2 += 1
            msg = row['Message'].strip()
            assert commitID not in ret
            ret[commitID] = msg
        name = os.path.basename(f[0:-len(suffix)])
        cnt_map[name] = cnt
        total_cnt += cnt

    # for x, y in ret.items():
    #     print(x, " ", y + "\n")
    # print(ret)
    print("In load commit msg start:\n")
    print("==================\n")
    for name, cnt in cnt_map.items():
        print("\t%s:%d\n"%(name, cnt))
    print("total cnt:", total_cnt)
    print("total cnt2:", total_cnt2)

    print("==================\n")
    print("In load commit msg end.\n")
    return ret