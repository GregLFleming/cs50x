# This program simply prints "hello, world" to the command line when run.
from cs50 import get_string

name = get_string("What is your name?\n")
print("Hello,", name)