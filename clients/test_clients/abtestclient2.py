'''
 AUTHOR: Gabriel Bassett
 DATE: 07-15-2013
 DEPENDANCIES: twisted, autobahn
 Copyright 2013 Gabriel Bassett

 LICENSE:
 This program is free software:  you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 or the LIcense, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public LIcense for more dtails.

 You should have received a copy of the GNU General Public License
 along with theis program.  If not, see <http://www.gnu.org/licenses/>.

 ACKNOWLEDGEMENTS:
 Based on autobahn client reference code, Copyright 2011,2012 Tavendo GmbH
 Licensed under the Apache License, Version 2.0

 DESCRIPTION:
 Basic test client to test sending DCES events to the pubsub server

 TODO:
 

 NOTES:
 

'''

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
      self.prefix("moirai", "http://%s/%s/" % (app_domain, app_name))

      # shortname for the domain + app name + topic
      GraphAddr = "moirai:graph" + topicId

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
