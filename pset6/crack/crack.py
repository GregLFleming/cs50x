import sys
from crypt import crypt
from itertools import product
from string import ascii_lowercase
from string import ascii_uppercase

# brute force solves for a password using a provided hash


def main():
    # check for ONE hashed password entry
    if len(sys.argv) != 2:
        print("Enter ONLY one hashed password (no spaces)")
        return(1)
        # define salt and library to characters to check for
    given_hash = sys.argv[1]
    salt = given_hash[:2]
    alphabet = ascii_uppercase + ascii_lowercase

    # brute force iterate through every combination of letters
    for i in range(6):
        for j in product(alphabet, repeat=i):
            testword = ''.join(j)
            if given_hash == crypt(testword, salt):
                print("Password found: ", end="")
                print(testword)
                return(0)
    print("Password not found.")
    return(1)


if __name__ == "__main__":
    main()