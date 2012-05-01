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

class Document(object):
    def __init__(self, root=None):
        self.root = root
        self.history_buffer = []
    
    def pack(self):
        s = []
        for i in self.history_buffer:
            s.append(json.dumps([i[0], i[1], i[2].pack()]))
        return '\n'.join(s)

    @classmethod
    def unpack(self, type, data):
        pass

    def exclude_operation(self, operation):
        # ensure that this operation actually happened.
        assert operation._id in [i[2]._id for i in self.history_buffer]

        inverse_of_op = None

        to_unroll = []
        for hb in reversed(self.history_buffer):
            to_unroll.append( hb )
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

            mutated_unroll = self.mutate_based_on(x.root.clone(), path, to_unroll, operation)

            for ots, opath, forward, backward in mutated_unroll:
                new, rev = forward.apply(x.root.get_path(opath))
                x.root.set_path(opath, new)
                x.history_buffer.append([ots, opath, forward, rev])

            return x

    def mutate_based_on(self, root, tpath, oplist, reference_op):
        target_node = root.get_path(tpath)
        if reference_op == None:
            return reversed(oplist)
        else:
            if target_node.type in (trees.TYPES['number'], trees.TYPES['boolean'], trees.TYPES['null']):
                # these ops do not have pathing or children.
                return reversed(oplist)
            elif target_node.type in (trees.TYPES['list'], trees.TYPES['string']):
                new_list = []

                for ts, path, operation, reverse in oplist:
                    p = operation.clone()
                    
                    if tpath and tpath != path: #if there is a path to the target
                        if all([i == j for i,j in zip(tpath, path)]):
                            if type(reference_op) == ops.ListInsertOperation:
                                path[len(tpath)] = safe_bound(path[len(tpath)] + len(reference_op.value))
                            elif type(reference_op) == ops.ListDeleteOperation:
                                path[len(tpath)] = safe_bound(path[len(tpath)] - reference_op.length)

                            elif type(reference_op) == ops.StringInsertOperation:
                                p.index = safe_bound(p.index + len(reference_op.text))
                                operation = p
                            elif type(reference_op) == ops.StringDeleteOperation:
                                p.index = safe_bound(p.index - reference_op.length)
                                operation = p
                        new_list.append([ts, path, operation, reverse])
                    else:
                        if reference_op.index > operation.index:
                            pass
                        else:
                            if type(reference_op) == ops.ListInsertOperation:
                                p.index = safe_bound(p.index + len(reference_op.value))
                            elif type(reference_op) == ops.ListDeleteOperation:
                                p.index = safe_bound(p.index - reference_op.length)

                            elif type(reference_op) == ops.StringInsertOperation:
                                p.index = safe_bound(p.index + len(reference_op.text))
                            elif type(reference_op) == ops.StringDeleteOperation:
                                p.index = safe_bound(p.index - reference_op.length)

                        newroot, newrev = p.apply(root)
                        new_list.append([ts, path, p, newrev])
                        root = newroot
                return reversed(new_list)
            elif target_node.type == trees.TYPES['dict']:
                # right now this isn't anything, but in order to handle key changes or moves
                # this will need to be implemented. If not, then this can be left as is.
                return reverse(oplist)
            else:
                return reverse(oplist)
