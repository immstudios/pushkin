import os
from nxtools import *

class PushkinFile(object):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path
        self.base_name = os.path.basename(path)
        self.data = None

        if not os.path.isfile(path):
            raise IOError

        self.mtime = os.path.getmtime(path)
        self.published = False

    def load_data(self):
        self.data = self.get_data()

    def get_data(self):
        return open(self.path, "rb").read()

    def publish(self, **kwargs):
        if self.parent.publish_file(self, **kwargs):
            self.published = True
            return True
        logging.warning("Publishing {} failed".format(self))
        return False

    def __len__(self):
        return self.is_valid

    def __repr__(self):
        return "<{}>".format(self.base_name)
