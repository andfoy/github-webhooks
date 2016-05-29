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
        filename = "./output.log"
        file_2 = './err.log'
        self.proc = Subprocess(["tail", "-f", filename, "-n", "0"],
                               stdout=Subprocess.STREAM,
                               bufsize=1)
        self.proc2 = Subprocess(["tail", "-f", file_2, "-n", "0"],
                               stdout=Subprocess.STREAM,
                               bufsize=1)
        self.proc.set_exit_callback(self._close)
        self.proc.stdout.read_until("\n", self.write_output)
        self.proc2.set_exit_callback(self._close)
        self.proc2.stdout.read_until("\n", self.write_err)

    @tornado.gen.coroutine
    def _close(self, *args, **kwargs):
        self.proc.proc.terminate()
        self.proc.proc.wait()
        self.proc2.proc.terminate()
        self.proc2.proc.wait()

    @tornado.gen.coroutine
    def add_listener(self, _id, sock):
        self.sockets[_id] = sock

    @tornado.gen.coroutine
    def remove_listener(self, _id):
        del self.sockets[_id]
    
    @tornado.gen.coroutine
    def write_output(self, data):
        msg = json.dumps({'type':'out', 'msg':data.strip()})
        for _id in self.sockets:
            self.sockets[_id].notify(msg)
        self.proc.stdout.read_until("\n", self.write_output)

    @tornado.gen.coroutine
    def write_err(self, data):
        msg = json.dumps({'type':'err', 'msg':data.strip()})
        for _id in self.sockets:
            self.sockets[_id].notify(msg)
        self.proc2.stdout.read_until("\n", self.write_err)    

