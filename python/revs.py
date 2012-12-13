## The following should be used for both the HMS version and the
## consistent history versions. the revision/commit process
## should look something like this.
## Revision (None for root) -> Commit([changes]) -> Revision 1 (node).

import trees
import ops


class Revision(object):
    def __init__(self, data, commit=None):
        #if none this is ROOT
        self.node = data

        #if none this is HEAD
        self.next_commit = commit


class Commit(object):
    def __init__(self, prev_rev=None, changes=None):
        #previous revision (assuming current revision is HEAD,
        #excluding 'changes' results in previous revision)
        self.prev_revision = prev_rev

        #changes in order to get to next revision.
        self.changes = changes or []


def examples():
    r = Revision(trees.Node.from_obj(10))
    c1 = Commit(r, [ops.NumberIncrementOperation(10)])
