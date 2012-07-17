import uuid
import trees
import hashlib

class Commit(object):
    def __init__(self, uid=None):
        if (uid == None):
            uid = str(uuid.uuid4())
        self.uid = uid

    def gen_next_commit(self, operation):
        h = hashlib.md5()
        h.update(self.uid)
        h.update(operation._id)
        return Commit(uid=h.hexdigest())


class HistoryManager(object):
    def __init__(self):
        self.commit_table = {}
        self.head_commit = None
        self.snapshot = None
        
    def init_value(self, py_value):
        t = obj_to_json_type(py_value)
        self.snapshot = trees.Node.from_obj(py_value)
        self.head_commit = Commit().uid

    def apply(self, operation):
        next_id = self.head_commit.gen_next_commit(operation)
        if next_id in self.commit_table:
            # we already have this in our state.
            pass
        else:
            # we need to find the parent, and branch.
            if operation.target_commit not in self.commit_table:
                if operation.target_commit == self.head_commit:
                    #we don't know of any changes after this commit
                    #so it will become the new head of the HMS.

                    new_head = self.head_commit.gen_next_commit(operation)
                    self.commit_table[self.head_commit] = operation._id
                    self.snapshot, reverse = operation.apply(self.snapshot)
                    self.head_commit = new_head
                else:
                    #this commit is for a previous version, so we need
                    #to compensate for the changes that have occured
                    #since it was created.

                    cur_transform = self.commit_table[operation.target_commit]
                    operation = operation.cross_merge(cur_transform)
