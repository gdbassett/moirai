###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol


# STATIC VARIABLES
app_domain = "informationsecurityanalytics.com"
app_name = "moirai"

ws_host = "localhost"
ws_port = "9000"



class PubSubClient1(WampClientProtocol):

   def onSessionOpen(self):
      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s#" % (app_domain, app_name))

      print "Subscribing to %s at port %s" % (app_name, ws_port)

      # Suscribe to the pubsub
      self.subscribe("moirai:graph1", self.onApp)

   def onSimpleEvent(self, topicUri, event):
      print "Event", topicUri, event

   def onApp(self, topicUri, event):
      print app_name, topicUri, event


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = WampClientFactory("ws://%s:%s" % (ws_host, ws_port), debugWamp = debug)
   factory.protocol = PubSubClient1

   connectWS(factory)

   reactor.run()
