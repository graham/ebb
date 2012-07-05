import unittest


def arg_split(s, sp=None, pu=None):
    splitters = sp or [' ']
    pushers = pu or ['"', "'"]
    level = 0

    news = []
    buf = []
    last = ''
    for i in s:
        if i in splitters and not level:
            news.append(''.join(buf))
            buf = []
        elif (i in pushers) and (not level) and (last in splitters):
            level = i
            news.append(''.join(buf))
            buf = []
        elif level:
            if i == level:
                level = ''
                news.append(''.join(buf))
                buf = []
            else:
                buf.append(i)
        else:
            buf.append(i)

        last = i

    if buf:
        news.append(''.join(buf))

    return filter(lambda x: x, news)


class TestUtil(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(arg_split('this is a "small test"'),
                         ['this', 'is', 'a', 'small test'])

    def test_nested(self):
        self.assertEqual(
            arg_split('this is "another test \'to\' see" what happens'),
            ['this', 'is', "another test 'to' see", 'what', 'happens'])

    def test_non_split(self):
        self.assertEqual(arg_split("graham's strings should not split"),
                         ["graham's", 'strings', 'should', 'not', 'split'])

if __name__ == '__main__':
    unittest.main()
