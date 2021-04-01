def get_string_width(multi_string):
    lines = multi_string.split("\n")
    max_width = 0
    for l in lines:
        len_l = len(l)

        if max_width < len_l:
            max_width = len_l

    return max_width
