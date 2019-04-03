from __future__ import absolute_import
import abc


class Database(object):
    __metaclass__ = abc.ABCMeta

    FIELD_MEMBER_FIRST_NAME = 'member_firstname'
    FIELD_MEMBER_LAST_NAME = 'member_lastname'
    FIELD_MEMBER_PERSON_ID = 'person_id'
    FIELD_MEMBER_EXTERNAL_ID = 'member_external_id'
    FIELD_MEMBER_FACE_ID = 'member_face_id'
    FIELD_MEMBER_FACE_ENCODING = 'member_face_encoding'
    FIELD_MEMEBER_EMAIL = 'member_email'
    FIELD_MEMEBER_PHONE = 'member_phone'
    FIELD_HASH = 'hash'

    # Name of your Database subclass, this is used in configuration
    # to refer to your class
    type = None

    def __init__(self):
        super(Database, self).__init__()

    def before_fork(self):
        """
        Called before the database instance is given to the new process
        """
        pass

    def after_fork(self):
        """
        Called after the database instance has been given to the new process

        This will be called in the new process.
        """
        pass

    def setup(self):
        """
        Called on creation or shortly afterwards.
        """
        pass

    @abc.abstractmethod
    def empty(self):
        """
        Called when the database should be cleared of all data.
        """
        pass

    
    @abc.abstractmethod
    def get_member_by_id(self, pid):
        """
        
        pid: person identifier
        """
        pass
    
    @abc.abstractmethod
    def get_member_attendance_by_personid(self, pid):
        """
        
        pid: person identifier
        """
        pass
    
    @abc.abstractmethod
    def get_member_encoded_face(self):
        """
        
        """
        pass

    @abc.abstractmethod
    def insert_attendance(self, param):
        """
        Inserts 
          param: 
        """
        pass

    @abc.abstractmethod
    def insert_member(self, params):
        """
        Inserts a member into the database, returns the person
        identifier of the member.

        praram: firstname, lastname, email, phone.
        """
        pass

    @abc.abstractmethod
    def update_member_external_id(self, params):
        """
        Update a member externalid,

        praram: externalid.
        """
        pass

    @abc.abstractmethod
    def query(self, hash):
        """
        Returns all matching fingerprint entries associated with
        the given hash as parameter.

        hash: Part of a sha1 hash, in hexadecimal format
        """
        pass

    
def get_database(database_type=None):
    # Default to using the mysql database
    database_type = database_type or "mysql"
    # Lower all the input.
    database_type = database_type.lower()

    for db_cls in Database.__subclasses__():
        if db_cls.type == database_type:
            return db_cls

    raise TypeError("Unsupported database type supplied.")


# Import our default database handler
import ElRoiApp.roi_backbone.database_sql
