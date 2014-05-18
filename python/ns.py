import trees
import ops
import time
import json
import os
import shutil
import hashlib
import sqlite3
from document import Document


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
        self.dirty_docs = {}
        self.dirty_ops = []

    def execute(self, key, path, operation):
        if key in self.docs:
            doc = self.docs[key]
        else:
            doc = self.constructor()

        newd = doc.include_operation(path, operation)
        ts, _path, _forward, _backward = newd.history_buffer[-1]

        self.dirty_docs[key] = (newd, operation._id)
        self.dirty_ops.append([ts, key, path, operation])

        self.docs[key] = newd
        return newd

    def flush(self):
        for key in self.dirty_docs:
            value, prev_op = self.dirty_docs[key]
            self.save_revision(key, prev_op, value)
            self.save_document(key)

        for ts, key, path, op in self.dirty_ops:
            self.save_op(key, path, op, ts)

        self.dirty_docs = {}
        self.dirty_ops = []

    def save_revision(self, key, prev_op, value):
        raise Exception("Someone didn't implement save_revision")

    def save_op(self, key, path, op):
        raise Exception("Someone didn't implement save_op")

    def save_document(self, key):
        raise Exception("Someone didn't implement save_document")

    def load_document(self, key):
        raise Exception("Someone didn't implement load_doc")

    def load_revision(self, key, revision):
        raise Exception("Someone didn't implement load_revision")

    def load_op(self, op_id):
        raise Exception("Someone didn't implement load_op")

    def list_keys(self):
        return []

    def get(self, key):
        return self.docs[key]

    def get_value(self, key):
        return self.docs[key].root.obj_repr()


# ignore this for now
class NamespaceFS(Namespace):
    ## These can be in a synced environment.
    SYNC_ROOT = '/tmp/data/'
    DIR_WITH_CHANGES = 'ops'
    DIR_WITH_CURRENT_STATE = 'revision'

    ## These cannot because they are specific to the state of this client.
    META_ROOT = '/tmp/local/'
    DIR_WITH_META_STATE = 'meta'

    def full_load(self):
        self.docs = {}
        self.dirty_docs = {}
        self.dirty_ops = []

        self.load_local_state()
        self.check_for_changes()

    def check_for_changes(self):
        path_to_ops = '%s/%s' % (self.SYNC_ROOT, self.DIR_WITH_CHANGES)
        for i in os.listdir(path_to_ops):
            op_id, key, path, packed_op, ts = self.load_op(i)
            if key not in self.docs:
                ## we have a key we don't know about.
                pass
            else:
                ## we know about this key.
                op = ops.Operation.unpack(packed_op)
                self.dirty_ops.append((ts, key, path, op))
                if not self.docs[key].history_includes_operation(op):
                    self.docs[key] = self.docs[key].include_operation(path, op, ts=ts)
                    #self.dirty_docs[key] = self.docs[key], op._id

    def load_local_state(self):
        path_to_docs = '%s/%s' % (self.META_ROOT, self.DIR_WITH_META_STATE)
        for i in os.listdir(path_to_docs):
            self.load_document(i)

    def save_document(self, key):
        hkey = hashlib.md5(key).hexdigest()
        path_to_docs = '%s/%s' % (self.META_ROOT, self.DIR_WITH_META_STATE)
        file_path = '%s/%s' % (path_to_docs, hkey)
        doc = self.get(key)
        f = open(file_path, 'w')
        f.write(json.dumps([key, doc.pack()]))
        f.close()

    def load_document(self, hkey):
        path_to_docs = '%s/%s' % (self.META_ROOT, self.DIR_WITH_META_STATE)
        file_path = '%s/%s' % (path_to_docs, hkey)
        data = open(file_path).read()
        key, doc_hb = json.loads(data)
        assert hkey == hashlib.md5(key).hexdigest()
        doc = self.constructor.unpack(json.loads(doc_hb))
        self.docs[key] = doc

    def load_revision(self, key, revision):
        path_to_keys = '%s/%s' % (self.SYNC_ROOT, self.DIR_WITH_CURRENT_STATE)
        return json.loads(open('%s/%s_%s' % (path_to_keys, key, revision)).read())

    def save_revision(self, key, prev_op, value):
        hkey = hashlib.md5(key).hexdigest()
        path = '%s/%s/%s_%s' % (self.SYNC_ROOT, self.DIR_WITH_CURRENT_STATE, hkey, prev_op)
        f = open(path, 'w')
        f.write(json.dumps([hkey, prev_op, key, value.root.obj_repr()]))
        f.close()

    def load_op(self, rev_id):
        path_to_ops = '%s/%s' % (self.SYNC_ROOT, self.DIR_WITH_CHANGES)
        return json.loads(open('%s/%s' % (path_to_ops, rev_id)).read())

    def save_op(self, key, path, op, ts):
        file_path = '%s/%s/%s' % (self.SYNC_ROOT, self.DIR_WITH_CHANGES, op._id)
        f = open(file_path, 'w')
        f.write(json.dumps([op._id, key, path, op.pack(), ts]))
        f.close()

    def list_keys(self):
        all_keys = os.listdir(path_to_keys)

        d = {}
        for i in all_keys:
            hkey, rev = i.split('_')
            if hkey in d:
                d[hkey].append(rev)
            else:
                d[hkey] = [rev]

        return d

    def init(self):
        for i in (self.SYNC_ROOT,
                  '%s/%s' % (self.SYNC_ROOT, self.DIR_WITH_CHANGES),
                  '%s/%s' % (self.SYNC_ROOT, self.DIR_WITH_CURRENT_STATE),
                  self.META_ROOT,
                  '%s/%s' % (self.META_ROOT, self.DIR_WITH_META_STATE)):
            if not os.path.isdir(i):
                os.mkdir(i)

    def purge(self):
        if os.path.isdir(self.SYNC_ROOT):
            shutil.rmtree(self.SYNC_ROOT)
        if os.path.isdir(self.META_ROOT):
            shutil.rmtree(self.META_ROOT)
    

class NamespaceSQLite(NamespaceFS):
    SYNC_DB = '/tmp/data.db'
    TABLE_CHANGES_NAME = 'ops'
    TABLE_CHANGES_DEF = '''
create table %s (
 uid int primary key,
 key varchar(1024),
 op_id varchar(128),
 path text,
 value text
)''' % TABLE_CHANGES_NAME

    TABLE_CURRENT_NAME = 'revisions'
    TABLE_CURRENT_DEF = '''
create table %s (
 uid int primary key,
 key varchar(1024),
 prev_op varchar(128),
 value text
)''' % TABLE_CURRENT_NAME

    META_DB = '/tmp/meta.db'
    TABLE_STATE_NAME = 'current_state'
    TABLE_STATE_DEF = '''
create table %s (
 uid int primary key,
 key varchar(1024),
 current varchar(1024)
)''' % TABLE_STATE_NAME

    def table_exists(self, cursor, title):
        q = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';" % title
        cursor.execute(q)
        result = q.fetchone()
        if result is None:
            return False
        else:
            return True

    def init(self):
        self.sync_db = sqlite3.connect(self.SYNC_DB)
        self.meta_db = sqlite3.connect(self.META_DB)

        csdb = self.sync_db.cursor()
        if not self.table_exists(csdb, TABLE_CHANGES_DEF):
            csdb.execute(TABLE_CHANGES_DEF)
        if not self.table_exists(csdb, TABLE_CURRENT_DEF):
            csdb.execute(TABLE_CURRENT_DEF)
        self.sync_db.commit()

        cmdb = self.meta_db.cursor()
        if not self.table_exists(cmdb, TABLE_STATE_DEF):
            cmdb.execute(TABLE_STATE_DEF)
        self.meta_db.commit()

    def purge(self):
        csdb = self.sync_db.cursor()
        if self.table_exists(csdb, TABLE_CHANGES_DEF):
            csdb.execute('delete from %s' % TABLE_CHANGES_NAME)
        if self.table_exists(csdb, TABLE_CURRENT_DEF):
            csdb.execute('delete from %s' % TABLE_CURRENT_NAME)
        self.sync_db.commit()

        cmdb = self.meta_db.cursor()
        if self.table_exists(cmdb, TABLE_STATE_DEF):
            cmdb.execute('delete from %s' % TABLE_STATE_NAME)
        self.meta_db.commit()

    def save_revision(self, key, prev_op, value):
        hkey = hashlib.md5(key).hexdigest()
        cursor = self.sync_db.cursor()
        cursor.execute('insert into %s(key, prev_op, value) ' +
                       'values(?, ?, ?);' %
                       TABLE_CURRENT_NAME, [hkey, prev_op, json.dumps(value)])
        self.sync_db.commit()

    def save_op(self, key, path, op):
        cursor = self.sync_db.cursor()
        cursor.execute('insert into %s(key, op_id, path, value) ' +
                       'values(?, ?, ?, ?);' %
                       TABLE_CHANGES_NAME, [key, op._id, path, op.pack()])
        self.sync_db.commit()
