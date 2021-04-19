
# def process(checkFunc):
#     print("Start process!\n")
#     msg_replace_cnt = 0
#     abandon_cnt = 0
#     all_cnt = len(ALL_APPLY_COMMITS)
#
#     print("All cnt of commits:%d" % all_cnt)
#
#     for i, commit in enumerate(ALL_APPLY_COMMITS, 1):
#         need_print = commit.commit_id == '8c4a905ce247333b5950bd2f03cf103e34533db8'
#         if commit.is_orphan:
#             continue
#         if not checkFunc(commit):
#             continue
#         if need_print:
#             print("CCCC1", commit.commit_id in COMMIT_MSG_MAP)
#         if commit.commit_id in COMMIT_MSG_MAP:
#             new_msg = COMMIT_MSG_MAP[commit.commit_id]
#             commit.new_message = new_msg
#             msg_replace_cnt += 1
#         if need_print:
#             print("CCCC2:$%s$" % commit.new_message)
#             print("CCCC3:$%s$" % COMMIT_MSG_MAP[commit.commit_id])
#         # anbandon by manually
#
#         if commit.new_message == "":
#             abandon_cnt += 1
#             continue
#
#         # if need_print:
#         #     break
#         # copy_commit(REPO, NEW_REPO, commit)
#         # progress_bar_output(i, all_cnt)
#
#     print("Total replace msg cnt:%d\n" % msg_replace_cnt)
#     print("Abandon cnt:%d\n" % abandon_cnt)
#     print("\nProcess done!\n")