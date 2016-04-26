# -*- coding: iso-8859-15 -*-

import os
import sys
import hmac
import hashlib
import tornado.web
import tornado.escape

class HookHandler(tornado.web.RequestHandler):
    def initialize(self, some_attribute=None):
        self.digestmod = hashlib.sha1

    @tornado.gen.coroutine
    def get(self):
        self.write("Github Webhook Server is running")

    @tornado.gen.coroutine
    def post(self):
        correct = True
        try:
           print self.request.headers['X-GitHub-Event']
           key = self.request.headers['X-Hub-Signature']
           correct = self.verify_signature(key, self.request.body)
        except KeyError:
           self.set_status(403)
           correct = False
        if correct:
           data = tornado.escape.json_decode(self.request.body)
           print data['repository']['name']

    def verify_signature(self, key, msg):
        key1 = hmac.HMAC(self.application.signature, msg, self.digestmod).hexdigest()
        key = key[5:]
        return sum(i != j for i, j in zip(key1, key)) == 0



