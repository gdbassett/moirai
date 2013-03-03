###############################################################################
##
##  Copyright 2011 Tavendo GmbH
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
##  Code Updated by Gabriel Bassett 2-27

import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol

# Static Variables:
app_domain = "informationsecurityanalytics.com"
app_name = "moirai"
topicId = "1"

# Location of ws server
ws_host = "localhost"
ws_port = "9000"

testDict = {'an': {'21': {'b': 0.6901961, 'g': 0.7882353, 'Degree': 4, 'Label': 'Sends phishing email asking for info to be mailed back or entered into website.', 'r': 0.4745098, 'y': -350.97687, 'x': 307.24896, 'z': 0, 'CPT': '{"nodeId":21,"index":["18",true,false],"1":[1,"1","0"],"0":[0,"0","1"]}', 'Class': 'Event', 'size': 42.4}}}



class MyClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Publish & Subscribe (PubSub) with Autobahn WebSockets.
   """

   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc = e.value.args
      print "ERROR: %s ('%s')" % (erroruri, errodesc)

   def done(self, *args):
      self.sendClose()

   def onApp(self, topicUri, event):
      print app_name, topicUri, event

   def onSessionOpen(self):
      print "Session Opened"

      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s#" % (app_domain, app_name))

      # shortname for the domain + app name + topic
      GraphAddr = "moirai:graph1"

      print "Subscribing to " + GraphAddr
      self.subscribe(GraphAddr, self.onApp)

      # lets try and publish something
      self.publish(GraphAddr, {"an":{"C":{"label":"DOMAIN","Class":"Attribute","Metadata":{"DOMAIN":"fark.com"}}}})
      self.publish(GraphAddr, {"an":{"C":{"label":"DOMAIN","Class":"Attribute","Metadata":{"DOMAIN":"fark.com"}, "bool": True}}})
      self.publish(GraphAddr, {"an":{"C":{"label":"DOMAIN","Class":"Attribute","Metadata":{"DOMAIN":"fark.com"}, "size":0.5}}})
      self.publish(GraphAddr, testDict)

      # quit after publishing
      self.done()


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://" + ws_host + ":" + ws_port)
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
