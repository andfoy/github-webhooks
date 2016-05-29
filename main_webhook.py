#!/usr/bin/env python

import os
import sys
import log
import base64
import webhook
import tornado.web
import tornado.ioloop
import websocket_handler


clr = 'clear'
if os.name == 'nt':
   clr = 'cls'

def main():
  secret = os.environ.get('WEBHOOK_SECRET')
  if not secret:
     print "Webhook secret variable must be defined in the current environment"
     sys.exit(-1)
  secret = base64.b64decode(secret)
  application = tornado.web.Application([(r"/", webhook.HookHandler),
              (r"/log", websocket_handler.WebSocketHandler)],
              debug=True, serve_traceback=True, autoreload=True)
  print "Server is now at: 127.0.0.1:8000"
  ioloop = tornado.ioloop.IOLoop.instance()
  log_mon = log.LogMonitor()
  application.log_mon = log_mon
  application.signature = secret
  application.listen(8000)
  try:
    ioloop.start()
  except KeyboardInterrupt:
    pass
  finally:
    print "Closing server...\n"
    application.log_mon._close()
    tornado.ioloop.IOLoop.instance().stop()

if __name__ == '__main__':
   os.system(clr)
   main()
