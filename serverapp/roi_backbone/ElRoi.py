# -*- coding: utf-8 -*-

__author__ = """Christopher David"""
__email__ = 'chris.dj.sam@gmail.com'
__version__ = '1.0.0'

from ElRoiApp.roi_backbone.database import get_database, Database

from ElRoiApp.roi_backbone.api import load_image_file, face_locations, batch_face_locations, face_landmarks, face_encodings, compare_faces, face_distance

class ElRoi(object):

    def __init__(self, config):
        super(ElRoi, self).__init__

        self.config = config

         # initialize db
        db_cls = get_database(config.get("database_type", None))

        self.db = db_cls(**config.get("database", {}))
        self.db.setup()
