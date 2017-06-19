import os
import json
import requests

class Pushkin(object):
    def __init__(souce_dir, publish_url, **kwargs):
        self.souce_dir = souce_dir
        self.publish_url = publish_url
        self.settings = kwargs

        if not os.path.isdir(self.souce_dir):
            raise IOError("Source directory {} does not exist".format(self.souce_dir))

        self.should_run = True
        if self.settings.get("blocking", True):
            self.work()
        else:
            thread.start_new_thread(self.work,())

    def stop(self):
        self.should_run = False

    def work(self):
        while self.should_run:
            self.main()
            time.sleep(self.settings.get("loop_delay", .5))

    def main(self):
        for fname in os.listdir(self.source_dir):
            source_path = os.path.join(self.source_dir, fname)




