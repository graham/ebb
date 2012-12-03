import json

DEBUG = 1

TYPES = {
    'number':0,
    'string':1,
    'boolean':2,
    'list':3,
    'dict':4,
    'null':5
}

APPLY_TYPES = [
    TYPES['number'],
    TYPES['boolean'],
    TYPES['null']
]

#I've thought quite a bit about having more data types, things like
#sets, sorted_sets, packed_sets, 

def obj_to_json_type(k):
    if type(k) in (int, long, float, bool):
        return 'number'
    elif type(k) in (str, unicode):
        return 'string'
    elif type(k) in (bool,):
        return 'bool'
    elif type(k) in (list, ):
        return 'list'
    elif type(k) in (dict, ):
        return 'dict'
    elif k == None:
        return 'null'
    elif type(k) in (Node,):
        return 'node'
    else:
        raise Exception('unknown type %r' % str(type(k)))

def type_for_enum(k):
    for i in TYPES:
        if TYPES[i] == k:
            return i

class Node(object):
    def __init__(self, **kwargs):
        self.name = None
        self.type = None
        self.attr = {}

        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'type' in kwargs:
            self.type = TYPES[kwargs['type']]
        elif 'type_id' in kwargs:
            self.type = kwargs['type_id']
        if 'attr' in kwargs:
            self.attr = kwargs['attr']

        self.value = None
        self.children = []

    def clone(self):
        return Node.from_obj(self.obj_repr())

    @classmethod
    def from_obj(cls, obj):
        t = obj_to_json_type(obj)
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
        elif t == 'dict':
            n = Node(type='dict')
            for k in obj:
                v = obj[k]
                nn = Node.from_obj(v)
                nn.attr['key'] = k
                n.children.append(nn)
            return n
        elif t == 'null':
            n = Node(type='null')
            return n
        elif t == 'node':
            return obj

    def __repr__(self):
        if DEBUG:
            return "<Node t:%s attr:%r value:%r children:%r>" % (
                type_for_enum(self.type), self.attr, self.value, self.children)
        else:
            return "<Node t:%s attr:%r value:%r children:%i>" % (
                type_for_enum(self.type), self.attr, self.value, len(self.children))

    def obj_repr(self):
        if self.type == TYPES['number']:
            if self.value == None:
                self.value = json.dumps(0)
            return json.loads(self.value)
        elif self.type == TYPES['string']:
            if self.value == None:
                self.value = json.dumps('')
            return json.loads(self.value)
        elif self.type == TYPES['boolean']:
            if self.value == None:
                self.value = json.dumps(False)
            return json.loads(self.value)
        elif self.type == TYPES['list']:
            return [i.obj_repr() for i in self.children]
        elif self.type == TYPES['dict']:
            return dict([(i.attr['key'], i.obj_repr()) for i in self.children])
        elif self.type == TYPES['null']:
            return None
        else:
            raise Exception("%i is not defined in the TYPES table" % self.type)


    @classmethod
    def default_for_type(self, t):
        if t == TYPES['number']:
            return 0
        elif t == TYPES['string']:
            return ''
        elif t == TYPES['boolean']:
            return False
        elif t == TYPES['list']:
            return []
        elif t == TYPES['dict']:
            return dict()
        elif t == TYPES['null']:
            return None
        else:
            raise Exception("%i is not defined in the TYPES table" % t)

    def set_value(self, obj):
        if type(obj) in (int, long, float, bool, str, unicode):
            self.value = json.dumps(obj)
        elif type(obj) in (Node,):
            if obj.value != None:
                self.value = obj.value
            if obj.children != None:
                self.children = obj.children
            else:
                raise Exception("Bad set value")
        else:
            self.value = None

    ## Nice things to have for testing.
    def test_path(self, key):
        if not key:
            return True
        if len(key) == 1:
            return self._test(key[0])
        else:
            obj = self._test(key[0])
            if type(obj) == bool:
                return obj
            return obj.test_path(key[1:])

    def _test(self, key):
        if self.type == TYPES['dict']:
            for i in self.children:
                if key == i.attr['key']:
                    return True
            return False
        elif type(key) in (int, long):
            if self.type == TYPES['string']:
                return True
            elif self.type == TYPES['list']:
                return True
            else:
                return False
        else:
            return False

    def get_path(self, key):
        if not key:
            return self
        if len(key) == 1:
            return self._get(key[0])
        else:
            obj = self._get(key[0])
            return obj.get_path(key[1:])

    def _get(self, key):
        if self.type == TYPES['dict']:
            for i in self.children:
                if key == i.attr['key']:
                    return i
            raise Exception('key not found %s' % key)
        elif type(key) in (int, long):
            if self.type == TYPES['string']:
                return self.value[int(key)]
            elif self.type == TYPES['list']:
                return self.children[int(key)]
            else:
                raise Exception('Invalid path: cannot index type %s' % self.type)
        else:
            raise Exception('invalid path')

    def set_path(self, key, val):
        if not key:
            return self.set_value(val)
        if len(key) == 1:
            return self._set(key[0], val)
        else:
            obj = self._get(key[0])
            return obj.set_path(key[1:], val)

    def _set(self, key, value):
        if self.type == TYPES['dict']:
            for i in self.children:
                if key == i.attr['key']:
                    i.set_value(value)
                    return

            #looks like we didn't find the key
            if type(value) != Node:
                n = Node(type=obj_to_json_type(value))
            else:
                n = value.clone()
            n.attr['key'] = key
            n.set_value(value)
            self.children.append(n)
            return n
        elif type(key) in (int, long):
            if self.type == TYPES['string']:
                self.value[int(key)] = value
            elif self.type == TYPES['list']:
                if int(key) > len(self.children):
                    self.children.insert(int(key), Node.from_obj(value))
                else:
                    self.children[int(key)] = Node.from_obj(value)
            else:
                raise Exception('Invalid path: cannot index type %s' % self.type)
        else:
            raise Exception('invalid path')

    def remove_path(self, key):
        if len(key) == 1:
            return self._remove(key[0])
        else:
            obj = self._get(key[0])
            return obj.remove_path(key[1:])

    def _remove(self, key):
        if self.type == TYPES['dict']:
            new_children = []
            for i in self.children:
                if key != i.attr['key']:
                    new_children.append(i);
            self.children = new_children;
        elif type(key) in (int, long):
            if self.type == TYPES['string']:
                raise Exception('not supported')
            elif self.type == TYPES['list']:
                ikey = int(key)
                if ikey == 0:
                    self.children = self.children[ikey+1:]
                else:
                    self.children = self.children[:ikey] + self.children[ikey+1:]
            else:
                raise Exception('Invalid path: cannot index type %s' % self.type)
        else:
            raise Exception('invalid path')
