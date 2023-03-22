from cs50 import get_string
from sys import argv


def main():

    # check for 2 items entered on command line
    if len(argv) != 2:
        exit("Usage: python bleep.py dictionary")

    # accepts the words from the dictionary, arranges them into a list
    dictionary_path = argv[1]
    dictionary = open(dictionary_path, "r")
    banned_wordlist = set()
    for line in dictionary:
        banned_wordlist.add(line.rstrip("\n"))
    dictionary.close()

    # accepts message fromt he user, puts it into a list
    s = get_string("What message would you like to censor?\n")
    wordlist = s.split(' ')

    # checks each word in the message against the banned word list. If a banned word is found, a "*" is printed for every letter
    # in the word. If a banned word is not found, the original word is printed.
    for i in wordlist:
        if i.lower() in banned_wordlist:
            for j in i:
                print("*", end="")
            print("", end=" ")
        else:
            print(i, end=" ")
    print("")


if __name__ == "__main__":
    main()
