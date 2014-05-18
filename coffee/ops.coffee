# OT for your JSON data.

# A OPERATION is a type of change.

# Operations are described as follows:
#  op = [
#          int     for_type -- list, str, number, * (all)
#          str     name,    -- insert, incr, rename
#          void   *function -- actual function pointer
#       ]
# 

# A MODIFICATION is an instance of a operation
# that is assigned to a target object and a
# specific path (within the object)

# Modifications are described as follows:
#  mod = [
#          uuid    mod_id,
#          op      name,
#          str     key,
#          list    path_to_node,
#          args    blob
#        ]
#

# Now, it would be easy to stop there, but we have to have
# some sort of understanding about how we do ordering.
# As you grow into more than two forks parent_id makes
# some transformations extremely easy to deal with.
# however, timestamp is a easy way to solve the issue.
# (hold your assumptions until after you've read about
# rulesets).
# 
#  mod += [
#          ts      int,
#          parent  obj_rev_id
#        ]
#

# An object is a value (either partial or complete)
# of a key at a specific state. Application of a mod
# on an object will result in another unique object
# that
#
#  obj = [
#          str   namespace,
#          str   key,
#          node *root_node,
#          uuid  rev_id,
#          uuid  ruleset
#        ]
# 

# On the surface this is all fine and dandy, however,
# it doesn't allow for very much extensibility, datatypes
# are hardcoded into the system (json only) and you have
# no permission system.
#
# Enter the rule system.
#
# For now, assume this is in something like scheme to make
# it easy, but this could be in a number of easy to use DSLs.

# A ruleset is defined as:
#  ruleset = [
#        uuid  ruleset_id
#        void *func
#       ]

# A ruleset is simply a function that accepts two arguments:
# 
#   current_state
#   operation
#   
# and returns one of three results:
# 
#   1  = The operation is valid and should be committed to
#        the revision history.
#   0  = The operation is invalid and should not be committed
#        to the revision history.
#  -1  = An error occurred and you should retry this against
#        the ruleset at a future time.
#        (closed app, too long, power off, etc)
# 
# it can be as complex as you want, but understand that on
# some platforms this may result in a failure of a operation
# being applied. There are some common gotchas that people
# should avoid, like not allowing a operation because it's
# too old (you can't know when an operation will be applied
# so this would not be deterministic. I'll go more into
# depth in this in some sort of whitepaper.

# Once a modification passes the rule test, it should be
# committed and the updated state should be available to the
# user, but NEVER before that is true, even if it means that
# you provide old data. The system should never give out data
# that is not valid.
# 
# A key value store (with value introspection) is powerful but
# has the issue that it is not as searchable or auto-indexed
# (where as something like SQLite provides this)
#
# As a result, it is likely that an additional index that is
# searchable would be rather importan for larger data sets
# but perhaps not as important for smaller ones. One possibility
# would be a cached view similar to couchdb.

# Views
# A VIEW is described as follows
#  view = [
#      str   name,
#      str   re_match,
#      void *function
#    ]
#
# A view is a stored set of uuids that is updated whenever
# a 'key' for an object that has been modified is matched
# to the view itself. This means that the more views you have
# the longer it will take to manage additional updates.
#
# As a result, these views should be only used when needed
# and pruned (when not locked) to make sure they do not grow
# too large. Pruning of these views should be user definable
# (either by size, or explicitly by object [queues]) as well
# as atomic to edits (a deleted item should be removed from)
# all views that contain its uuid.

# op that does nothing
OP_NONCE    = 0

# basic data type targets
OP_ALL      = 1  # Ops of this type will work on any type.
OP_BOOLEAN  = 2  # Ops on booleans
OP_NUMBER   = 3  # Ops on numbers (int, float)
OP_STRING   = 4  # Ops on strings
OP_LIST     = 5  # Ops on lists
OP_HASHMAP  = 6  # Ops on hashmaps

# Add on data types [for later]
OP_SET      = 7  # list of only unique items.
OP_ZSET     = 8  # set with a rankable value (see redis zset).
OP_CAP_LIST = 9  # size capped list.
OP_GEO      = 10 # geo location (support move?).
OP_FILE     = 11 # allows for reads, seeks, writes.
OP_JOURNAL  = 12 # only allows appends and doesn't sync back to each client.

