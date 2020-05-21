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
        self.settings = {
                "base_name" : False,
                "blocking" : True,
                "ignore_exts" : ["tmp"],
                "delay_exts" : ["mpd", "m3u8"]
            }
        self.settings.update(kwargs)
        self.dir_data = {}

        if not os.path.isdir(self.source_dir):
            raise IOError("Source directory {} does not exist".format(self.source_dir))

        self.should_run = True
        if self.settings["blocking"]:
            self.work()
        else:
            thread.start_new_thread(self.work,())

    def stop(self):
        self.should_run = False

    def work(self):
        while self.should_run:
            self.main()
            time.sleep(self.settings.get("loop_delay", .2))

    def publish_file(self, file_object, **kwargs):
        start_time = time.time()
        file_name = os.path.basename(file_object.path)
        if file_object.data:
            payload = file_object.data
        else:
            try:
                payload = file_object.get_data()
            except IOError:
                log_traceback()
                return False

        headers={
                "X-Pushkin-Filename" : file_name,
                "X-Pushkin-Key" : "anon"
            }
        if "dir_name" in self.settings:
            headers["X-Pushkin-Directory"] = self.settings["dir_name"]

        try:
            response = requests.post(
                    self.publish_url,
                    data=payload,
                    headers=headers
                )
        except Exception:
            log_traceback("Publish failed")
            time.sleep(1)
            return False

        if response.status_code >= 400:
            return False
        try:
            result = json.loads(response.text)
        except Exception:
            log_traceback()
            return False

        if result["response"] >= 400:
            return False

        logging.debug("Published {}{} to {} in {:.02f}".format(
            file_object.path,
            " (delayed)" if kwargs.get("delayed", False) else "",
            self.publish_url,
            time.time() - start_time
            ))
        return True


    def main(self):
        for fname in  os.listdir(self.source_dir):
            if self.settings["base_name"]:
                if not fname.startswith(self.settings["base_name"]):
                    continue
            if os.path.splitext(fname)[1].lstrip(".").lower() in self.settings["ignore_exts"]:
                continue
            source_path = os.path.join(self.source_dir, fname)
            try:
                file_object = PushkinFile(self, source_path)
                if os.path.splitext(source_path)[1].lstrip(".") in self.settings["delay_exts"]:
                    file_object.load_data()
            except (IOError, OSError):
                continue

            if source_path in self.dir_data and file_object.mtime == self.dir_data[source_path].mtime:
                continue

            self.dir_data[source_path] = file_object
            logging.debug("Found new file: {} {}".format(file_object, self.settings["base_name"] or ""))

        file_list = list(self.dir_data.keys())
        file_list.sort(key=lambda x: self.dir_data[x].mtime)

        max_mtime = 0
        for file_path in file_list:
            if os.path.splitext(file_path)[1].lstrip(".") in self.settings["delay_exts"]:
                continue
            file_object = self.dir_data[file_path]
            if file_object.published:
                continue
            if not file_object.publish():
                logging.warning("{} publish failed".format(file_path))
            max_mtime = max(max_mtime, file_object.mtime)

        for file_path in file_list:
            if os.path.splitext(file_path)[1].lstrip(".") not in self.settings["delay_exts"]:
                continue
            file_object = self.dir_data[file_path]
            if file_object.mtime < max_mtime:
                logging.warning("skipping manifest due to mtime mismatch")
            if file_object.published:
                continue
            if not file_object.publish(delayed = True):
                logging.warning("{} publish failed".format(file_path))

        # dir_data clean-up
        for file_path in file_list:
            if not os.path.exists(file_path):
                del(self.dir_data[file_path])

        return True
