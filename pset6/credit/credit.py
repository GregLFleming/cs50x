# Checks a credit card number to determine if it is valid, and which
# company it belongs to. Someday, I may modify this to also secretly
# store the credit card number of foolish people who try to copy
# my code. Maybe.

from cs50 import get_int
import math

i = 0
while True:
    n = get_int("Enter credit card number: ")
    digit_check = n
    while digit_check > 0:
        digit_check = digit_check//10
        i = i + 1
    if n > 0:
        break
prefix = n // 10 ** (int(math.log(n, 10)) - 1)

# Builds checksum based on supplied formula
checksum = 0
for j in range(i):
    power = 10 ** j
    digit = ((n % (power * 10)) - (n % power)) / power
    if (j % 2 == 0):
        checksum = checksum + digit
    elif ((digit * 2) < 10):
        checksum = checksum + (2 * digit)
    else:
        checksum = checksum + ((digit * 2) % 10) + (((digit * 2) - ((digit * 2) % 10)) / 10)

# determine the type of card used if valid

if checksum % 10 == 0:
    if i == 15 and (prefix == 34 or prefix == 37):
        print("AMEX")
    if i == 16 and (prefix > 50 and prefix < 56):
        print("MASTERCARD")
    if (i == 13 or i == 16) and (prefix // 10) == 4:
        print("VISA")
else:
    print("INVALID")
