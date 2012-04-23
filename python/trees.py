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

    def proto(self, value=None, children=None):
        p = Node(name=self.name, type_id=self.type, attr=self.attr)
        if value != None:
            p.set_value(value)
        if children != None:
            p.children = children
        return p

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

    def set_value(self, obj):
        if type(obj) in (int, long, float, bool, str, unicode):
            self.value = json.dumps(obj)
        elif type(obj) in (Node,):
            self.value = obj.value
        else:
            self.children = Node.from_obj(obj)

    ## Nice things to have for testing.

    def get_path(self, key, di='.'):
        sp = key.split(di)
        if len(sp) == 1:
            return self._get(sp[0])
        else:
            obj = self._get(sp[0])
            return obj.get_path(di.join(sp[1:]))

    def _get(self, key):
        if self.type == TYPES['dict']:
            for i in self.children:
                if key == i.attr['key']:
                    return i
            raise Exception('key not found %s' % key)
        elif key.isdigit():
            if self.type == TYPES['string']:
                return self.value[int(key)]
            elif self.type == TYPES['list']:
                return self.children[int(key)]
            else:
                raise Exception('Invalid path: cannot index type %s' % self.type)
        else:
            raise Exception('invalid path')

    def set_path(self, key, val, di='.'):
        sp = key.split(di)
        if len(sp) == 1:
            return self._set(sp[0], val)
        else:
            obj = self._get(sp[0])
            return obj.set_path(di.join(sp[1:]), val)

    def _set(self, key, value):
        if self.type == TYPES['dict']:
            for i in self.children:
                if key == i.attr['key']:
                    i.set_value(value)
                    return

            #looks like we didn't find the key
            n = Node(type=obj_to_json_type(value))
            n.attr['key'] = key
            n.set_value(value)
            self.children.append(n)
            return n
        elif key.isdigit():
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

    def remove_path(self, key, di='.'):
        sp = key.split(di)
        if len(sp) == 1:
            return self._remove(sp[0])
        else:
            obj = self._get(sp[0])
            return obj.remove_path(di.join(sp[1:]))

    def _remove(self, key):
        if self.type == TYPES['dict']:
            new_children = []
            for i in self.children:
                if key != i.attr['key']:
                    new_children.append(i);
            self.children = new_children;
        elif key.isdigit():
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
