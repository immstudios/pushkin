import os
import time
import json
import requests

from nxtools import *

from .pushkin_file import PushkinFile


class Pushkin(object):
    def __init__(self, source_dir, publish_url, **kwargs):
        self.source_dir = source_dir
        self.publish_url = publish_url
        self.settings = kwargs
        self.dir_data = {}

        if not os.path.isdir(self.source_dir):
            raise IOError("Source directory {} does not exist".format(self.source_dir))

        self.should_run = True
        if self.settings.get("blocking", True):
            self.work()
        else:
            thread.start_new_thread(self.work,())

    def stop(self):
        self.should_run = False

    def work(self):
        while self.should_run:
            if self.main():
                time.sleep(self.settings.get("loop_delay", .5))
            else:
                time.sleep(.1)

    def publish_file(self, path):
        logging.debug("Publishing {} to {}".format(path, self.publish_url))
        file_name = os.path.basename(path)
        payload = open(path, "rb").read()

        response = requests.post(
            self.publish_url,
            data=payload,
            headers={
                    "X-Pushkin-Filename" : file_name,
                    "X-Pushkin-Key" : "anon"
                }
            )

        if response.status_code >= 400:
            return False
        try:
            result = json.loads(response.text)
        except Exception:
            log_traceback()
            return False

        if result["response"] >= 400:
            return False
        return True


    def main(self):
        for fname in  os.listdir(self.source_dir):
            source_path = os.path.join(self.source_dir, fname)
            if source_path in self.dir_data:
                continue
            try:
                self.dir_data[source_path] = PushkinFile(self, source_path)
            except IOError:
                continue
            logging.debug("Found new file: {}".format(source_path))

        file_list = self.dir_data.keys()
        file_list.sort(key=lambda x: self.dir_data[x].mtime)

        for file_path in file_list:
            file_object = self.dir_data[file_path]
            if file_object.published:
                print "already published"
                continue
            if not file_object.publish():
                logging.warning("{} publish failed".format(file_path))
                return False

        # dir_data clean-up
        for file_path in file_list:
            if not os.path.exists(file_path):
                del(self.dir_data[file_path])

        return True
