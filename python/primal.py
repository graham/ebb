import math

def gen_primes():
    def is_prime(n):
        if n == 2:
            return True

        for i in range(3, int(math.sqrt(n))):
            if n % i == 0:
                return False

        return True

    def gen():
        yield 2
        n = 3
        while True:
            if is_prime(n):
                yield n
            n += 2
                               
    return gen()


class Doc(object):
    def __init__(self):
        self.p = gen_primes()
        self.pvis = 1

    def __repr__(self):
        return "<Doc rev: %i>" % self.pvis

    def inject_version(self, id):
        self.pvis *= id
    
    def next_rev(self):
        while True:
            n = self.p.next()
            if not self.is_child_of(n):
                self.pvis *= n
                return

    def is_child_of(self, id):
        if self.pvis % id == 0:
            return True
        else:
            return False


