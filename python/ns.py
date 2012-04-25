import trees
import ops
import time
import json

class Namespace(object):
    def __init__(self, name):
        self.name = name
        self.docs = {}

    def execute(self, key, operation):
        if key in self.docs:
            doc = self.docs[key]
        else:
            doc = Document()
        newd = doc.include_operation(key, operation)
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

        x = Document(self.root)

        for hb in self.history_buffer:
            if hb[2]._id != operation._id:
                x.history_buffer.append(hb)
            else:
                break

        # replay the 

        for ts, path, forward, backward in to_unroll:
            new, rev = backward.apply(x.root)
            x.root = new

        mutated_unroll = self.mutate_based_on(x.root.proto(), inverse_of_op[1], to_unroll[:-1], inverse_of_op[3])

        for ts, path, forward, backward in mutated_unroll:
            new, rev = forward.apply(x.root)
            x.root = new
            x.history_buffer.append([ts, path, forward, rev])

        return x

    def include_operation(self, path, operation, ts=None):
        #make sure that the operation has not been included yet.
        assert operation._id not in [i[2]._id for i in self.history_buffer]

        if self.root == None:
            self.root = trees.Node(type=operation.for_type)

        if ts == None:
            ts = time.time()
            new, reverse = operation.apply(self.root)
            x = Document(new)
            for i in self.history_buffer:
                x.history_buffer.append(i)
            x.history_buffer.append([ts, path, operation, reverse])
            return x
        else:
            to_unroll = []
            for hb in reversed(self.history_buffer):
                if ts < hb[0]:
                    to_unroll.append(hb)

            x = Document(self.root)

            for hb in self.history_buffer:
                if ts >= hb[0]:
                    x.history_buffer.append(hb)
                else:
                    break

            for ots, opath, forward, backward in to_unroll:
                new, rev = backward.apply(x.root)
                x.root = new

            new, rev = operation.apply(x.root)
            x.root = new
            x.history_buffer.append([ts, path, operation, rev])

            mutated_unroll = self.mutate_based_on(x.root.proto(), path, to_unroll, operation)

            for ots, opath, forward, backward in mutated_unroll:
                new, rev = forward.apply(x.root)
                x.root = new
                x.history_buffer.append([ots, opath, forward, rev])

            return x

    def mutate_based_on(self, root, path, oplist, reference_op):
        if reference_op == None:
            return oplist
        else:
            if reference_op.for_type == 'number':
                return oplist
            elif reference_op.for_type == 'string':
                new_list = []
                for ts, path, operation, reverse in oplist:
                    p = operation.proto()

                    if reference_op.index > operation.index:
                        pass # this happened after don't care
                    else:
                        if type(reference_op) == ops.StringInsertOperation:
                            p.index += len(reference_op.text)
                        elif type(reference_op) == ops.StringDeleteOperation:
                            p.index -= reference_op.length

                    root, newrev = p.apply(root)
                    new_list.append([ts, path, p, newrev])
                return new_list
            elif reference_op.for_type == 'list':
                new_list = []
                for ts, path, operation, reverse in oplist:
                    p = operation.proto()

                    if reference_op.index > operation.index:
                        pass # this happened after don't care
                    else:
                        if type(reference_op) == ops.ListInsertOperation:
                            p.index += len(reference_op.value)
                        elif type(reference_op) == ops.ListDeleteOperation:
                            p.index -= reference_op.length

                    root, newrev = p.apply(root)
                    new_list.append([ts, path, p, newrev])
                return new_list
            else:
                return oplist
