import json

DEBUG = 1

TYPES = {
    'number':0,
    'string':1,
    'boolean':2,
    'list':3,
    'hash':4,
    'null':5
}

def python_to_json_type(k):
    if type(k) in (int, float, bool):
        return 'number'
    elif type(k) in (str, unicode):
        return 'string'
    elif type(k) in (list, ):
        return 'list'
    elif type(k) in (dict, ):
        return 'hash'
    elif k == None:
        return 'null'
    else:
        raise Exception('unknown type %r' % str(type(k)))

def type_for_enum(k):
    for i in TYPES:
        if TYPES[i] == k:
            return i

class Node(object):
    def __init__(self, **kwargs):
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'type' in kwargs:
            self.type = TYPES[kwargs['type']]
        self.attr = {}
        self.value = None
        self.children = []

    @classmethod
    def from_obj(cls, obj):
        t = python_to_json_type(obj)
        if t == 'number':
            n = Node(type='number')
            n.set_value(obj)
            return n
        elif t == 'string':
            n = Node(type='string')
            n.set_value(obj)
            return n
        elif t == 'boolean':
            n = Node(type='boolean')
            n.set_value(obj)
            return n
        elif t == 'list':
            n = Node(type='list')
            for i in obj:
                n.children.append(Node.from_obj(i))
            return n
        elif t == 'hash':
            n = Node(type='hash')
            for k in obj:
                v = obj[k]
                nn = Node.from_obj(v)
                nn.attr['key'] = k
                n.children.append(nn)
            return n
        elif t == 'null':
            n = Node(type='null')
            return n

    def __repr__(self):
        if DEBUG:
            return "<Node t:%s attr:%r value:%r children:%r>" % (
                type_for_enum(self.type), self.attr, self.value, self.children)
        else:
            return "<Node t:%s attr:%r value:%r children:%i>" % (
                type_for_enum(self.type), self.attr, self.value, len(self.children))

    def obj_repr(self):
        if self.type == TYPES['number']:
            return json.loads(self.value)
        elif self.type == TYPES['string']:
            return json.loads(self.value)
        elif self.type == TYPES['boolean']:
            return json.loads(self.value)
        elif self.type == TYPES['list']:
            return [i.obj_repr() for i in self.children]
        elif self.type == TYPES['hash']:
            return dict([(i.attr['key'], i.obj_repr()) for i in self.children])
        elif self.type == TYPES['null']:
            return None
        else:
            raise Exception("%i is not defined in the TYPES table" % self.type)

    def set_value(self, obj):
        if type(obj) in (int, float, bool, str, unicode):
            self.value = json.dumps(obj)
        else:
            self.children = Node.json(obj)

    ## Nice things to have for testing.

    def get_path(self, key, di='.'):
        sp = key.split(di)
        if len(sp) == 1:
            return self._get(sp[0])
        else:
            cur = sp[0]
            obj = self._get(cur)
            return obj.get_path(di.join(sp[1:]))

    def _get(self, key):
        if key.isdigit():
            if self.type == TYPES['string']:
                return self.value[int(key)]
            elif self.type == TYPES['list']:
                return self.children[int(key)]
            else:
                raise Exception('Invalid path: cannot index type %s' % self.type)
        elif self.type == TYPES['hash']:
            for i in self.children:
                if key == i.attr['key']:
                    return i
            raise Exception('key not found %s' % key)
        else:
            raise Exception('invalid path')
                

    def set_path(self, key, val, di='.'):
        sp = key.split(di)
        if len(sp) == 1:
            return self._set(sp[0], val)
        else:
            cur = sp[0]
            obj = self._get(cur)
            return obj.set_path(di.join(sp[1:]), val)

    def _set(self, key, value):
        if key.isdigit():
            if self.type == TYPES['string']:
                self.value[int(key)] = value
            elif self.type == TYPES['list']:
                self.children[int(key)] = value
            else:
                raise Exception('Invalid path: cannot index type %s' % self.type)
        elif self.type == TYPES['hash']:
            for i in self.children:
                if key == i.attr['key']:
                    i.set_value(value)
                    return

            #looks like we didn't find the key
            n = Node(type=python_to_json_type(value))
            n.attr['key'] = key
            n.set_value(value)
            self.children.append(n)
            return n
        else:
            raise Exception('invalid path')
        
