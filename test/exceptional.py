import sys
import re

if len(sys.argv) == 1:
    exit("Parameters are 'raise', 'good', N")

if sys.argv[1] == 'over':
    x = sys.argv[2]

if sys.argv[1] == 'raise':
    raise Exception("Something bad happened.")

if sys.argv[1] == 'good':
    exit()

if re.search(r'\A\d+\Z', sys.argv[1]):
    exit(int(sys.argv[1]))

exit(sys.argv[1])