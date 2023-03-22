def lines(a, b):
    """Return lines in both a and b"""

    # seperate strings "a" and "b" into lists "a_list" and "b_list" where each element is a line from "a" and "b"
    a_list = a.splitlines()
    b_list = b.splitlines()

    # convert lists into sets to remove repeat lines and give compare functionality
    a_set = set(a_list)
    b_set = set(b_list)

    # find similarities between set a and set b and store them in line_matches
    line_matches = a_set & b_set

    return line_matches


def sentences(a, b):
    """Return sentences in both a and b"""

    from nltk.tokenize import sent_tokenize
    # seperate strings "a" and "b" into lists "a_list" and "b_list" where each element is a sentence from "a" and "b"
    a_list = sent_tokenize(a)
    b_list = sent_tokenize(b)

    # convert lists into sets to remove repeat sentences and give compare functionality
    a_set = set(a_list)
    b_set = set(b_list)

    # find similarities between set a and set b and store them in line_matches
    sentence_matches = a_set & b_set

    return sentence_matches


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    # seperate strings "a" and "b" into lists "a_list" and "b_list" where each element is a substring from "a"
    # and "b" of length "n"

    a_list = []
    b_list = []

    for i in range(0, len(a) - n + 1):
        a_list.append(a[i: n + i])
    for i in range(0, len(b) - n + 1):
        b_list.append(b[i: n + i])

    # convert lists into sets to remove repeat sentences and give compare functionality
    a_set = set(a_list)
    b_set = set(b_list)

    # find similarities between set a and set b and store them in substring_matches
    substring_matches = a_set & b_set

    return substring_matches