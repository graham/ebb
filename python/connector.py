
## Table is as follows:
# uid    - hash defined at creation, this will never change,
#          used to refer to the object forever.
# cid    - canonical id, will change as soon as master assigns it 
#          (in resolution scenario this could happen more than once).
# parent - uid of the object for which the following 

table = '''
create table ebb_meta_int (
    local_cid int,
    last_known_gcid int
);

create table ebb_operation (
    uid varchar(%(hash_length)i) PRIMARY KEY NOT NULL,
    gcid int,
    parent varchar(%(hash_length)i),
    key varchar(%(hash_length)i),
    data varchar(%(hash_length)i)
);

create table ebb_snapshot (
    key varchar(%(hash_length)i) PRIMARY KEY NOT NULL,
    data varchar(%(hash_length)i),
    lcid varchar(%(hash_length)i)
);

create table ebb_data (
    id varchar(%(hash_length)i) PRIMARY KEY NOT NULL,
    data text
);

''' % {
    'hash_length':68
    }
## The plug is your connection to the data.
class Plug(object):
    def __init__(self):
        self.db = None

    # 
    def sync(self, callback=None):
        pass
