from __future__ import absolute_import
from itertools import zip_longest
import queue as Queue

import MySQLdb as mysql
from MySQLdb.cursors import DictCursor

from ElRoiApp.roi_backbone.database import Database


class SQLDatabase(Database):
    
    type = "mysql"

    # tables
    MEMBERS_TABLENAME = "tbl_members"
    MEMBERS_FACE_TABLENAME = "tbl_member_faces"
    MEMBERS_ATTENDANCE_TABLENAME = "tbl_register_timestamp"


    # default variables
    PARAMS = ()

    # creates
    CREATE_MEMBERS_TABLE = """
        CREATE TABLE IF NOT EXISTS %s (member_id smallint unsigned not null auto_increment, member_firstname varchar(35) NOT NULL, 
        member_lastname varchar(35), member_email varchar(100), member_phone varchar(15), member_external_id int, member_created DATETIME DEFAULT CURRENT_TIMESTAMP, 
        person_id varchar(50) NOT NULL, PRIMARY KEY (member_id)) ENGINE=INNODB;""" % (
        MEMBERS_TABLENAME
    )

    CREATE_FACES_TABLE = """
        CREATE TABLE IF NOT EXISTS %s (`id`	smallint unsigned not null auto_increment,`person_id` varchar(50) NOT NULL,
        `member_face_id` varchar(50),`member_face_encoding` BLOB, `member_face_created` DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id))
        ENGINE=INNODB;""" % (
        MEMBERS_FACE_TABLENAME,
    )

    CREATE_ATTENDANCE_TABLE = """
        CREATE TABLE IF NOT EXISTS %s (`id`	smallint unsigned not null auto_increment, 
        `person_id`	varchar(50) NOT NULL, `timestamp` DATETIME DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id)) ENGINE=INNODB;
        """ % (
            MEMBERS_ATTENDANCE_TABLENAME,
        )

    # inserts (ignores duplicates)
    INSERT_MEMEBER = """ INSERT INTO %s(%s,  %s, %s, %s, %s, %s) VALUES(%%s, %%s, %%s, %%s, %%s, %%s); 
    """ % (MEMBERS_TABLENAME, Database.FIELD_MEMBER_FIRST_NAME, Database.FIELD_MEMBER_LAST_NAME, Database.FIELD_MEMEBER_EMAIL, Database.FIELD_MEMEBER_PHONE, Database.FIELD_MEMBER_PERSON_ID, Database.FIELD_MEMBER_EXTERNAL_ID)
    
    UPDATE_MEMBER = """ UPDATE %s set %s = %%s WHERE %s = %%s ; 
    """ % (MEMBERS_TABLENAME, Database.FIELD_MEMBER_EXTERNAL_ID, Database.FIELD_MEMBER_PERSON_ID)

    INSERT_FACE = """ INSERT INTO %s (%s, %s, %s) VALUES(%%s, %%s, %%s)
    """ % (MEMBERS_FACE_TABLENAME, Database.FIELD_MEMBER_PERSON_ID, Database.FIELD_MEMBER_FACE_ID, Database.FIELD_MEMBER_FACE_ENCODING )

    INSERT_ATTENDANCE = """ insert into %s (%s) values (%%s); """ % (MEMBERS_ATTENDANCE_TABLENAME, Database.FIELD_MEMBER_PERSON_ID)

    # selects queries
    SELECT_PERSONID = """
        SELECT %s from %s where %s = %%s and  %s = %%s
    """ % (Database.FIELD_MEMBER_PERSON_ID, MEMBERS_TABLENAME, Database.FIELD_MEMBER_FIRST_NAME, Database.FIELD_MEMBER_LAST_NAME)

    SELECT_MEMBERS_BYPERSONID = """
        SELECT %s from %s where %s = %%s 
    """ % (Database.FIELD_MEMBER_EXTERNAL_ID,MEMBERS_TABLENAME, Database.FIELD_MEMBER_PERSON_ID)

    SELECT_EXISTING_ATTENDANCE = """ SELECT * FROM %s WHERE %s = %%s and UNIX_TIMESTAMP(timestamp) > UNIX_TIMESTAMP(SUBDATE(NOW(), 1)); 
    """ % (MEMBERS_ATTENDANCE_TABLENAME, Database.FIELD_MEMBER_PERSON_ID)
    
    SELECT_ALL_MEMBER_FACE_ENCODING = """ SELECT a.%s, a.%s, b.%s, a.%s FROM %s a INNER JOIN %s b WHERE a.%s = b.%s 
    """ % (Database.FIELD_MEMBER_FIRST_NAME, Database.FIELD_MEMBER_LAST_NAME, Database.FIELD_MEMBER_FACE_ENCODING, Database.FIELD_MEMBER_PERSON_ID, MEMBERS_TABLENAME, MEMBERS_FACE_TABLENAME, Database.FIELD_MEMBER_PERSON_ID, Database.FIELD_MEMBER_PERSON_ID)

    SELECT_ALL_MEMBER_FACE_ENCODING_ID = """ SELECT a.%s, b.%s  FROM %s a INNER JOIN %s b WHERE a.%s = b.%s 
    """ % (Database.FIELD_MEMBER_PERSON_ID, Database.FIELD_MEMBER_FACE_ENCODING, MEMBERS_TABLENAME, MEMBERS_FACE_TABLENAME, Database.FIELD_MEMBER_PERSON_ID, Database.FIELD_MEMBER_PERSON_ID)

    def __init__(self, **options):
        super(SQLDatabase, self).__init__()
        self.cursor = cursor_factory(**options)
        self._options = options

    def after_fork(self):
        # Clear the cursor cache, we don't want any stale connections from
        # the previous process.
        Cursor.clear_cache()

    def setup(self):
        """
        Creates any non-existing tables required for El-Roi to function.

        """
        with self.cursor() as cur:
            cur.execute(self.CREATE_MEMBERS_TABLE)
            cur.execute(self.CREATE_FACES_TABLE)
            cur.execute(self.CREATE_ATTENDANCE_TABLE)

  
    def ismemberrecorded_by_personid(self, pid):
        """
        
        """
        isfound = False
        with self.cursor(cursor_type=DictCursor) as cur:
            print("{}".format(self.SELECT_EXISTING_ATTENDANCE, (pid,)))
            cur.execute(self.SELECT_EXISTING_ATTENDANCE, (pid,))
            for row in cur:
                if (row['person_id'] != ""):
                    isfound = row['person_id']
            return isfound

    def get_member_by_name(self, params):
        """
        Return songs that have the fingerprinted flag set TRUE (1).
        """
        memberid = ""
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_PERSONID, params)
            for row in cur:
                memberid = row['person_id']
            return memberid

    def get_member_by_id(self, pid):
        """
        Returns song by its ID.
        """
        externalid = ""
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_MEMBERS_BYPERSONID, (pid,))
            for row in cur:
                externalid = row[Database.FIELD_MEMBER_EXTERNAL_ID]
        return externalid

    def get_member_encoded_face(self):
        """
        Returns member firstname, lasname and encoded face
        """
        dataset = []
        with self.cursor(cursor_type=DictCursor) as cur:
            cur.execute(self.SELECT_ALL_MEMBER_FACE_ENCODING)
            for row in cur:
                dataset.append(row)
        return dataset
        
    
    def insert_attendance(self, params):
        """
        Inserts member in the database and returns the ID of the inserted record.
        """
        with self.cursor() as cur:
            cur.execute(self.INSERT_ATTENDANCE, params)
            return cur.lastrowid

    def update_member_external_id(self, params):
        """
        Update Members external id.
        """
        with self.cursor() as cur:
            cur.execute(self.UPDATE_MEMBER, params)
            
    def insert_faces(self, params):
        """
        Inserts song in the database and returns the ID of the inserted record.
        """
        with self.cursor() as cur:
            cur.execute(self.INSERT_FACE, params)
            return cur.lastrowid

    def insert_member(self, params):
        """
        Inserts song in the database and returns the ID of the inserted record.
        """
        with self.cursor() as cur:
            cur.execute(self.INSERT_MEMEBER, params)
            return cur.lastrowid

    def query(self, hash):
        """
        Return all tuples associated with hash.

        If hash is None, returns all entries in the
        database (be careful with that one!).
        """
        # select all if no key
        query = self.SELECT_ALL if hash is None else self.SELECT

        with self.cursor() as cur:
            cur.execute(query)
            for sid, offset in cur:
                yield (sid, offset)


    def return_matches(self, hashes):
        """
        Return the (song_id, offset_diff) tuples associated with
        a list of (sha1, sample_offset) values.
        """
        # Create a dictionary of hash => offset pairs for later lookups
        mapper = {}
        for hash, offset in hashes:
            mapper[hash.upper()] = offset

        # Get an iteratable of all the hashes we need
        values = mapper.keys()

        with self.cursor() as cur:
            for split_values in grouper(values, 1000):
                # Create our IN part of the query
                query = self.SELECT_MULTIPLE
                query = query % ', '.join(['UNHEX(%s)'] * len(split_values))

                cur.execute(query, split_values)

                for hash, sid, offset in cur:
                    # (sid, db_offset - song_sampled_offset)
                    yield (sid, offset - mapper[hash])

    def __getstate__(self):
        return (self._options,)

    def __setstate__(self, state):
        self._options, = state
        self.cursor = cursor_factory(**self._options)


def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return (filter(None, values) for values
            in zip_longest(fillvalue=fillvalue, *args))

def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
    
def cursor_factory(**factory_options):
    def cursor(**options):
        options.update(factory_options)
        return Cursor(**options)
    return cursor


class Cursor(object):
    """
    Establishes a connection to the database and returns an open cursor.


    ```python
    # Use as context manager
    with Cursor() as cur:
        cur.execute(query)
    ```
    """
    _cache = Queue.Queue(maxsize=5)

    def __init__(self, cursor_type=mysql.cursors.Cursor, **options):
        super(Cursor, self).__init__()

        try:
            conn = self._cache.get_nowait()
        except Queue.Empty:
            conn = mysql.connect(**options)
        else:
            # Ping the connection before using it from the cache.
            conn.ping(True)

        self.conn = conn
        self.conn.autocommit(False)
        self.cursor_type = cursor_type

    @classmethod
    def clear_cache(cls):
        cls._cache = Queue.Queue(maxsize=5)

    def __enter__(self):
        self.cursor = self.conn.cursor(self.cursor_type)
        return self.cursor

    def __exit__(self, extype, exvalue, traceback):
        # if we had a MySQL related error we try to rollback the cursor.
        if extype is mysql.MySQLError:
            self.cursor.rollback()

        self.cursor.close()
        self.conn.commit()

        # Put it back on the queue
        try:
            self._cache.put_nowait(self.conn)
        except Queue.Full:
            self.conn.close()
