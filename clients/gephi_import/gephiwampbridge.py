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
 Bridges between a gephi websocket and a moirai pubsub

 TODO:
 

 NOTES:
 

'''

GEPHI_SERVER_URL = "ws://ec2-54-242-250-189.compute-1.amazonaws.com:8080/workspace0"
GEPHI_TOPIC_URI = "http://informationsecurityanalytics.com/moirai/graph#"

import sys, json

from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.websocket import WebSocketClientFactory, \
                               WebSocketClientProtocol, \
                               connectWS, \
                               listenWS

from autobahn.wamp import WampServerFactory, \
                          WampServerProtocol



class GephiClientProtocol(WebSocketClientProtocol):

   def onOpen(self):
      print "connected to Gephi"

   def onMessage(self, msg, binary):
      if not binary:
         print "sending dispatch"
         obj = json.loads(msg)
         self.factory.broker.dispatch(GEPHI_TOPIC_URI + "1", obj)


class GephiBridgeProtocol(WampServerProtocol):

   def onSessionOpen(self):
      ## register a URI and all URIs having the string as prefix as PubSub topic
      self.registerForPubSub(GEPHI_TOPIC_URI, True)


class GephiBridgeFactory(WampServerFactory):

   protocol = GephiBridgeProtocol

   def startFactory(self):
      WampServerFactory.startFactory(self)
      reactor.callLater(5, self.connectGephi)

   def connectGephi(self):
      wsClientFactory = WebSocketClientFactory(GEPHI_SERVER_URL)
      wsClientFactory.protocol = GephiClientProtocol
      wsClientFactory.broker = self
      connectWS(wsClientFactory)


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'

   factory = GephiBridgeFactory("ws://localhost:9000", debugWamp = debug)
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)

   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)

   reactor.run()
