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
        self.repos = self.get_repository_list()

    def get_repository_list(self):
        repos = {}
        with open('repositories', 'rb') as fp:
             lines = fp.readlines()
        lines = [i.strip('\n') for i in lines]
        for line in lines:
            if line != '':
               pair = line.split(',')
               repos[pair[0]] = pair[1]
        return repos

    def update_repository_list(self, name, url):
        with open('repositories', 'a+') as fp:
             fp.write("\n%s,%s" % (name, url))

    @tornado.gen.coroutine
    def get(self):
        self.render("index.html")

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
           os.system('echo "(%s) Downloading repository latest revision..." >> output.log' % (data['repository']['name']))
           try:
              script = self.repos[data['repository']['name']]
              os.system('cd '+script+' && git pull >> /root/webhooks/output.log 2>> /root/webhooks/err.log')
           except KeyError:
              url = data['repository']['ssh_url']
              os.system("cd /root && git clone "+url+" >> /root/webhooks/output.log 2>> /root/webhooks/err.log")
              script = '/root/'+data['repository']['name']
              self.repos[data['repository']['name']] = script
              self.update_repository_list(data['repository']['name'], script)
           os.system('cd '+script+' && chmod 777 '+script+'/deploy.sh')
           os.system('cd '+script+' && ./deploy.sh >> /root/webhooks/output.log 2>> /root/webhooks/err.log')

    def verify_signature(self, key, msg):
        key1 = hmac.HMAC(self.application.signature, msg, self.digestmod).hexdigest()
        key = key[5:]
        return sum(i != j for i, j in zip(key1, key)) == 0
