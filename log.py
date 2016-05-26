# -*- coding: iso-8859-15 -*-

import os
import sys
import json
import tornado
import subprocess
import tornado.web
from tornado.process import Subprocess

class LogMonitor(object):
    def __init__(self):
        self.sockets = {}
        filename = "./webhook.out"
        self.proc = Subprocess(["tail", "-f", filename, "-n", "0"],
                               stdout=Subprocess.STREAM,
                               bufsize=1)
        self.proc.set_exit_callback(self._close)
        self.proc.stdout.read_until("\n", self.write_line)

    @tornado.gen.coroutine
    def _close(self, *args, **kwargs):
        self.proc.proc.terminate()
        self.proc.proc.wait()

    @tornado.gen.coroutine
    def add_listener(self, _id, sock):
        self.sockets[_id] = sock

    @tornado.gen.coroutine
    def remove_listener(self, _id):
        del self.sockets[_id]
    
    @tornado.gen.coroutine
    def write_line(self, data):
        for _id in self.sockets:
            self.sockets[_id].notify(data.strip())
        self.proc.stdout.read_until("\n", self.write_line)

