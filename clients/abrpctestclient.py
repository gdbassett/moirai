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
## Edited by Gabriel bassett 3/13

# IMPORTS
import sys
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


# STATIC VARIABLES
app_domain = "informationsecurityanalytics.com"
app_name = "moirai"

ws_host = "localhost"
ws_port = "9000"



class SimpleClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Remote Procedure Calls (RPC) with
   AutobahnPython and Twisted Deferreds.
   """

   def show(self, result):
      print "SUCCESS:", result

   def onMsg(self, topicUri, event):
      print app_name, topicUri, event


   def logerror(self, e):
      erroruri, errodesc, errordetails = e.value.args
      print "ERROR: %s ('%s') - %s" % (erroruri, errodesc, errordetails)

   def done(self, *args):
      self.sendClose()
      reactor.stop()

   def onSessionOpen(self):

      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s/" % (app_domain, app_name))

      # Subscribe to the graph so that we get the graph state
      self.subscribe("moirai:graph1", self.onMsg)

      # Set our static query for testing purposes
      query = "START n = node(*) RETURN *;"
      params = {}

      # Execute the RPC
      self.call("moirai:cypher", query, params).addCallback(self.show)

      # Test to see if this works
      self.call("moirai:getState")


############## STUFF HAPPENS HERE  #############

if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://%s:%s" % (ws_host, ws_port), debugWamp = True)
   factory.protocol = SimpleClientProtocol
   connectWS(factory)
   reactor.run()
