def scheme_reduce_value(env, t, data):
    if type(data) != str:
        return data
    elif t == 'number':
        if '.' in data or data.endswith('f'):
            return float(data.strip('f'))
        else:
            return int(data)
    elif t == 'string':
        return data % env
    else:
        return data

delay_eval = ['define', 'quote', 'begin']
def scheme_parse_symbol(content):
    if type(content) == tuple:
        return content
    elif type(content) == int:
        return ('number', str(content))
    elif content == None:
        return ('null', None)
    elif len(content) and content[0].isdigit():
        return ('number', content)
    else:
        return ('symbol', content)

def scheme_eval(block, env):
    de_this = 0
    result = []

    index = 0
    while index < len(block):
        type, data = block[index]
        if type == 'code':
            result.append(scheme_eval(data, env))
        else:
            if type == 'symbol':
                if data in delay_eval:
                    env.find(data)(block[index+1:], env)
                    return
                else:
                    result.append(env.find(data))
            else:
                result.append((type, data))
        index += 1

    if result and callable(result[0]):
        return scheme_parse_symbol(result[0](result[1:], env))
    else:
        return result

def easy_val(x):
    return map(lambda x: scheme_reduce_value(env, x[0], x[1]), x)

class Environment(dict):
    def __init__(self, values, outer=None, default=False):
        self.outer = outer

        if default:
            values['+'] = lambda x, env: ('number', sum(easy_val(x)))
            values['*'] = lambda x, env: ('number', reduce(lambda prev, cur: prev * cur, easy_val(x)))
    
            def p(s, env):
                result = []
                for i in s:
                    result.append(scheme_reduce_value(env, 'string', str(i[1])))
                print ' '.join(result)
            values['print'] = p

            def define(x, env):
                key = x[0][1]
                value = x[1][1]

                if x[1][0] == 'code':
                    env.set(key, scheme_eval(x[1][1], env))
                else:
                    env.set(key, x[1])
            values['define'] = define
            
            def begin(x, env):
                sub = Environment(values={}, outer=env)
                for i in x:
                    scheme_eval(i[1], sub)
            values['begin'] = begin

            values['quote'] = lambda x, env: x
            self.outer = Environment(values=values)
        else:
            self.update(values)

    def find(self, key):
        if key in self:
            return self.get(key)
        else:
            if self.outer != None:
                return self.outer.find(key)
            else:
                raise KeyError("Key: %s not found." % key)

    def set(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        obj = dict.__getitem__(self, key)
        if type(obj) == tuple:
            return obj[1]
        return obj


class CodeObject(object):
    string_push = ["'", '"', '|']

    def __init__(self, s):
        self.orig = s
        self.compiled = None

    def tokenize(self):
        if self.compiled:
            return
        else:
            code = []
            index = 0

            while index < len(self.orig):
                chunk, index = self.parse_chunk(self.orig, index)
                code.append(chunk)
            self.compiled = code[0][1]
            
    def parse_chunk(self, s, start_index):
        index = start_index

        current = []
        stack = None
        word_buf = []

        while index < len(s):
            if stack:
                if s[index] == stack:
                    current.append(('string', ''.join(word_buf)))
                    word_buf = []
                    stack = None
                else:
                    word_buf.append(s[index])
            else:
                if s[index] == '(':
                    code, new_index = self.parse_chunk(s, index+1)
                    current.append(code)
                    index = new_index
                elif s[index] == ')':
                    if word_buf:
                        current.append(scheme_parse_symbol(''.join(word_buf)))
                    return (('code', current), index+1)
                elif s[index] == ' ':
                    if word_buf:
                        current.append(scheme_parse_symbol(''.join(word_buf)))
                        word_buf = []
                elif s[index] in self.string_push:
                    assert word_buf == []
                    stack = s[index]
                else:
                    word_buf.append(s[index])
            index += 1

        return ('code', current), index

    def run(self, env):
        results = None
        for t, v in self.compiled:
            assert t == 'code'
            results = scheme_eval(v, env)
        if results:
            return results

def repl():
    env = Environment({}, default=True)

    print '-------- start repl --------'

    while True:
        try:
            d = raw_input('> ')
            if not d:
                continue
        except EOFError, ef:
            print ''
            return
        except KeyboardInterrupt, ki:
            print ''
            return

        y = CodeObject(d)
        y.tokenize()
        try:
            r = y.run(env)
            if r: print r[1]
        except Exception, e:
            import traceback
            traceback.print_exc()
            
if __name__ == '__main__':
    env = Environment({}, default=True)

    tests = [
        "(define result (+ 1 2))",
        "(print 'hello world')",
        "(begin (define x 1) (print (+ 123 123 123 x)))",
        "(print 'the final number is %(result)s')",
        ]
      
    for i in tests:
        c = CodeObject(i)
        c.tokenize()
        r = c.run(env)
        if r: print r[1]
