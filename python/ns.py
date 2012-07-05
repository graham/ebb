import trees
import ops
import time
import json

def safe_bound(x):
    if x > 0:
        return x
    else:
        return 0

class Namespace(object):
    def __init__(self, name):
        self.name = name
        self.docs = {}

    def execute(self, key, path, operation):
        if key in self.docs:
            doc = self.docs[key]
        else:
            doc = Document()
        newd = doc.include_operation(path, operation)
        self.docs[key] = newd

    def get(self, key):
        return self.docs[key]

    def get_value(self, key):
        return self.docs[key].root.obj_repr()

    def query(self, match, func):
        for i in self.docs:
            pass

    def apply(self, match, func):
        for i in self.docs:
            pass


class Document(object):
    def __init__(self, root=None):
        self.root = root
        self.history_buffer = []
    
    def pack(self):
        s = []
        for i in self.history_buffer:
            s.append(json.dumps([i[0], i[1], i[2].pack()]))
        return '\n'.join(s)

    def exclude_operation(self, operation):
        # ensure that this operation actually happened.
        assert operation._id in [i[2]._id for i in self.history_buffer]

        inverse_of_op = None

        to_unroll = []
        for hb in reversed(self.history_buffer):
            to_unroll.append(hb)
            if hb[2]._id == operation._id:
                inverse_of_op = hb
                break;

        x = Document(self.root.clone())

        for hb in self.history_buffer:
            if hb[2]._id != operation._id:
                x.history_buffer.append(hb)
            else:
                break

        # replay the 

        for ts, path, forward, backward in to_unroll:
            new, rev = backward.apply(x.root.get_path(path))
            x.root.set_path(path, new)

        mutated_unroll = self.mutate_based_on(x.root.clone(), inverse_of_op[1], to_unroll[:-1], inverse_of_op[3])

        for ts, path, forward, backward in mutated_unroll:
            new, rev = forward.apply(x.root.get_path(path))
            x.root.set_path(path, new)
            x.history_buffer.append([ts, path, forward, rev])

        return x

    def include_operation(self, path, operation, ts=None):
        #make sure that the operation has not been included yet.
        assert operation._id not in [i[2]._id for i in self.history_buffer]

        if self.root == None:
            self.root = trees.Node(type=operation.for_type)

        if ts == None:
            ts = time.time()

            target_root = self.root.clone()
            new, reverse = operation.apply(target_root.get_path(path))
            target_root.set_path(path, new)
            new = target_root
                
            x = Document(new.clone())
            for i in self.history_buffer:
                x.history_buffer.append(i)
            x.history_buffer.append([ts, path, operation, reverse])
            return x
        else:
            to_unroll = []
            for hb in reversed(self.history_buffer):
                if ts < hb[0]:
                    to_unroll.append(hb)

            x = Document(self.root.clone())

            for hb in self.history_buffer:
                if ts >= hb[0]:
                    x.history_buffer.append(hb)
                else:
                    break

            for ots, opath, forward, backward in to_unroll:
                new, rev = backward.apply(x.root.get_path(opath))
                x.root.set_path(opath, new)

            new, rev = operation.apply(x.root.get_path(path))
            x.root.set_path(path, new)
            x.history_buffer.append([ts, path, operation, rev])

            mutated_unroll = list(self.mutate_based_on(x.root.clone(), path, to_unroll, operation))

            for ots, opath, forward, backward in mutated_unroll:
                new, rev = forward.apply(x.root.get_path(opath))
                x.root.set_path(opath, new)
                x.history_buffer.append([ots, opath, forward, rev])

            return x

    def mutate_based_on(self, root, tpath, oplist, reference_op):
        target_node = root.get_path(tpath)

        if reference_op == None or target_node.type in trees.APPLY_TYPES:
            return reversed(oplist)
        
        if target_node.type in (trees.TYPES['string'], trees.TYPES['list']):
            return reversed(reference_op.handle_mutate(root, tpath, oplist))
        elif target_node.type in (trees.TYPES['dict'], ):
            return reversed(oplist)
        else:
            ## this is a problem.
            return reversed(oplist)
