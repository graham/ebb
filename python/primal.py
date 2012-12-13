import math
import sys


def is_prime(n):
    if n == 2:
        return True

    for i in range(3, int(math.sqrt(n))):
        if n % i == 0:
            return False

    return True


def gen_next_prime(prev):
    prev += 2
    while not is_prime(prev):
        prev += 2
    return prev


class Revision(object):
    def __init__(self):
        self.prev = 3
        self.current_revision = 2

    def __repr__(self):
        return "<Revision %i>" % sys.getsizeof(self.current_revision)

    def next_rev(self):
        self.prev = gen_next_prime(self.prev)
        return self.prev

    def include(self, revision):
        if self.current_revision % revision != 0:
            self.current_revision *= revision
            return True
        else:
            return False

    def exclude(self, revision):
        if self.current_revision % revision == 0:
            self.current_revision /= revision
            return True
        else:
            return False

    def test(self, revision):
        if self.current_revision % revision == 0:
            return True
        else:
            return False
