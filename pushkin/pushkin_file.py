import os

class PushkinFile(object):
    def __init__(self, parent, path):
        self.parent = parent
        self.path = path
        self.base_name = os.path.basename(path)

        if not os.path.isfile(path):
            raise IOError

        self.mtime = os.path.getmtime(path)
        self.published = False

    def publish(self):
        if self.parent.publish_file(self.path):
            self.published = True
            return True
        return False

    def __len__(self):
        return self.is_valid

    def __repr__(self):
        return "<{}>".format(self.base_name)
