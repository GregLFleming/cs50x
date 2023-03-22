# this program accepts user inputed layers and prints the correspondign pyramid to the screen

from cs50 import get_int

# prompt user for height from 1 - 23
while True:
    n = get_int("Height: ")
    if n > 0 and n < 9:
        break

# print pyramid to screen

for i in range(n):
    for j in range(n + 3 + i):
        if (j < n - i - 1) or (j == n + 1) or (j == n):
            print(" ", end="")
        else:
            print("#", end="")
    print()
