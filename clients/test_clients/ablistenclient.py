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
 Used to test the client's ability to receive DCES events by pubsub

 TODO:
 

 NOTES:
 

'''
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
