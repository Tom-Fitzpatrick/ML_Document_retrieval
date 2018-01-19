from operator import itemgetter


class MyPriorityQueue:

    def __init__(self):
        self.q = []

    def __iter__(self):
        for item in self.q:
            yield item

    def put(self, key, value):
        self.q.append((key, value))
        self.q = sorted(self.q, key=itemgetter(0), reverse=True)
        return (key, value)

    def pop(self):
        popped = self.q.pop(0)
        return popped

    def chop(self):
        chopped = self.q.pop()
        return chopped

    def values(self):
        values = []
        for x in self.q:
            values.append(x[1])
        return values

    def __str__(self) -> str:
        return str(self.q)

    def list(self):
        return self.q

    def length(self):
        return len(self.q)

    def lowest_rank(self):
        if self.q:
            return self.q[len(self.q) - 1][0]
        else:
            return 0

    def top_N(self, n):
        if len(self.q) > n:
            return self.q[:n]
        return self.q

    def is_empty(self):
        if self.q:
            return False
        return True
