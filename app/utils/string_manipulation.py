import string
import random


def random_string(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def truncate_string(string, length=15):
    return f"{string[:length]}..." if len(string) > length else string
