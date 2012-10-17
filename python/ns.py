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
    # Manages a set of keys, could feasibly have multiple
    # 'cursors' making modifications as well as having multiple
    # 'users' making modifications, generally speaking changes
    # will not cross a namespace boundry... generally.
    def __init__(self, name):
        self.name = name
        self.docs = {}
        self.constructor = Document
        self.dirty_docs = []
        self.dirty_ops = []

    def execute(self, key, path, operation):
        if key in self.docs:
            doc = self.docs[key]
        else:
            doc = self.constructor()
        newd = doc.include_operation(path, operation)

        self.dirty_docs.append([key, newd])
        self.dirty_ops.append([key, path, operation])

        self.docs[key] = newd
        return newd

    def flush(self):
        self.dirty_docs = []
        self.dirty_ops = []

    def get(self, key):
        return self.docs[key]

    def get_value(self, key):
        return self.docs[key].root.obj_repr()

#ignore this for now
# class NamespaceFS(Namespace):
#     ROOT = 'data/'
#     def flush(self):
#         for key, rev in self.dirty_docs:
#             path_to_key = self.ROOT + 'asdf'
#         for key, path, op in self.dirty_ops:
#             pass
#         self.dirty_docs = []
#         self.dirty_ops = []

class Document(object):
    # The object that we are storing data in,
    # for each key there is n documents, however,
    # each of these documents should have a shared parent
    # the only time they don't would be if
    #  a. something is seriously wrong.
    #  b. the shared parent has been garbage collected.
    def __init__(self, root=None):
        self.root = root
        self.history_buffer = []

    def pack(self):
        s = []
        for i in self.history_buffer:
            s.append(json.dumps([i[0], i[1], i[2].pack()]))
        return '\n'.join(s)
    
    def __str__(self):
        return str(self.root.obj_repr())
    def __repr__(self):
        return self.__str__()

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

        x = self.__class__(self.root.clone())

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
                
            x = self.__class__(new.clone())
            for i in self.history_buffer:
                x.history_buffer.append(i)
            x.history_buffer.append([ts, path, operation, reverse])
            return x
        else:
            to_unroll = []
            for hb in reversed(self.history_buffer):
                if ts < hb[0]:
                    to_unroll.append(hb)

            x = self.__class__(self.root.clone())

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

            mutated_unroll = self.mutate_based_on(x.root.clone(), path, to_unroll, operation)

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


