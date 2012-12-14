import ops
import trees
import time


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
        return "<Document value=%r>" % str(self.root.obj_repr())

    def __repr__(self):
        return self.__str__()

    def get(self, path):
        return self.root.get_path(path)

    def get_value(self, path):
        return self.get(path).obj_repr()

    def exclude_operation(self, operation):
        # ensure that this operation actually happened.
        assert self.history_includes_operation(operation)

        inverse_of_op = None

        to_unroll = []
        for hb in reversed(self.history_buffer):
            to_unroll.append(hb)
            if hb[2]._id == operation._id:
                inverse_of_op = hb
                break

        x = self.__class__(self.root.clone())

        for hb in self.history_buffer:
            if hb[2]._id != operation._id:
                x.history_buffer.append(hb)
            else:
                break

        for ts, path, forward, backward in to_unroll:
            new, rev = backward.apply(x.root.get_path(path))
            x.root.set_path(path, new)

        mutated_unroll = self.mutate_based_on(
            x.root.clone(),
            inverse_of_op[1],
            to_unroll[:-1],
            inverse_of_op[3])

        for ts, path, forward, backward in mutated_unroll:
            new, rev = forward.apply(x.root.get_path(path))
            x.root.set_path(path, new)
            x.history_buffer.append([ts, path, forward, rev])

        return x

    def history_includes_operation(self, operation):
        if operation._id in [i[2]._id for i in self.history_buffer]:
            return True
        else:
            return False

    def include_operation(self, path, operation, ts=None, parent_rev=None):
        if parent_rev is None:
            return self.include_operation_ts(path, operation, ts=ts)
        else:
            return self.include_operation_parent_rev(path,
                                                     operation,
                                                     parent_rev=parent_rev)

    def include_operation_parent_rev(self, path, operation, parent_rev=None):
        pass

    def include_operation_ts(self, path, operation, ts=None):
        #make sure that the operation has not been included yet.
        assert not self.history_includes_operation(operation)

        if self.root is None:
            if operation.for_type == '*':
                self.root = trees.Node.from_obj(operation.value)
            else:
                self.root = trees.Node(type=operation.for_type)

        if ts is None:
            ts = time.time()

            target_root = self.root.clone()

            if target_root.test_path(path):
                new, reverse = operation.apply(target_root.get_path(path))
            else:
                new, reverse = operation.apply(
                    trees.Node.from_obj(
                        trees.Node.default_for_type(
                            trees.TYPES[operation.for_type])))

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

            ### I'll have to backtrace and make sure this all is correct.
            ### not entirely sure why this is that way.
            # if target_root.test_path(path):
            #    new, reverse = operation.apply(target_root.get_path(path))
            # else:
            #    new, reverse = operation.apply(trees.Node.from_obj(
            #    trees.Node.default_for_type(trees.TYPES[operation.for_type])))

            new, rev = operation.apply(x.root.get_path(path))
            x.root.set_path(path, new)
            x.history_buffer.append([ts, path, operation, rev])

            mutated_unroll = self.mutate_based_on(
                x.root.clone(),
                path,
                to_unroll,
                operation)

            for ots, opath, forward, backward in mutated_unroll:
                new, rev = forward.apply(x.root.get_path(opath))
                x.root.set_path(opath, new)
                x.history_buffer.append([ots, opath, forward, rev])

            return x

    def mutate_based_on(self, root, tpath, oplist, reference_op):
        target_node = root.get_path(tpath)

        if reference_op is None or target_node.type in trees.APPLY_TYPES:
            return reversed(oplist)

        if target_node.type in (trees.TYPES['string'], trees.TYPES['list']):
            return reversed(reference_op.handle_mutate(root, tpath, oplist))
        elif target_node.type in (trees.TYPES['dict'], ):
            return reversed(reference_op.handle_mutate(root, tpath, oplist))
        else:
            ## this is a problem.
            return reversed(oplist)
