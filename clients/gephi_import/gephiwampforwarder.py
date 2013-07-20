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
 Receives events from a gephi websocket and publishes them to the pubsub

 TODO:
 

 NOTES:
 

'''
WAMP_SERVER_URL = "ws://localhost:9000"
GEPHI_SERVER_URL = "ws://ec2-54-242-250-189.compute-1.amazonaws.com:8080/workspace0"
GEPHI_TOPIC_URI = "http://informationsecurityanalytics.com/moirai/graph"


import sys, json

from twisted.python import log
from twisted.internet import reactor

from autobahn.websocket import WebSocketClientFactory, \
                               WebSocketClientProtocol, \
                               connectWS

from autobahn.wamp import WampClientFactory, \
                          WampClientProtocol



class GephiClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      print "connected to Gephi"

   def onMessage(self, msg, binary):
      if not binary:
         obj = json.loads(msg)
         self.factory.forwarder.publish(GEPHI_TOPIC_URI + "1", obj)


class GephiForwardingProtocol(WampClientProtocol):

   def onSessionOpen(self):
      print "connected to WAMP server"
      factory = WebSocketClientFactory(GEPHI_SERVER_URL)
      factory.protocol = GephiClientProtocol
      factory.forwarder = self
      connectWS(factory)



if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = WampClientFactory(WAMP_SERVER_URL, debugWamp = debug)
   factory.protocol = GephiForwardingProtocol

   connectWS(factory)

   reactor.run()
