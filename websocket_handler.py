# -*- coding: iso-8859-15 -*-

import os
import sys
import json
import time
import hashlib
import datetime
import tornado.web
import tornado.escape
import tornado.websocket

class WebSocketHandler(tornado.websocket.WebSocketHandler):
 
    def open(self, *args, **kwargs):
        # self.application.pc.add_event_listener(self)
        self._id = hashlib.md5(str(time.time())).hexdigest()[0:7] 
        self.application.log_mon.add_listener(self._id, self)
        print("WebSocket opened")

    def on_close(self):
        self.application.log_mon.remove_listener(self._id)
        print("WebSocket closed")
        #self.application.outq.remove_listener(self.sec_num)
        # self.application.pc.remove_event_listener(self)

    def on_message(self, message):
        print message

    def notify(self, message):
        self.write_message(message)