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
 Used to test basic server RPC functionality

 TODO:
 

 NOTES:
 

'''

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
   def nodesFirst(self, result):
      self.show(result)
      query2 = "START n=node(*) MATCH n-[r]->m RETURN r, ID(n), ID(m);"
      params = {}
      self.call("moirai:cypher", query2, params).addCallback(self.show)

   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc, errordetails = e.value.args
      print "ERROR: %s ('%s') - %s" % (erroruri, errodesc, errordetails)

   def done(self, *args):
      self.sendClose()
      reactor.stop()

   def onSessionOpen(self):

      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s/" % (app_domain, app_name))
      
      query = "START n=node(*) RETURN n;"

      params = {}
      self.call("moirai:cypher", query, params).addCallbacks(self.nodesFirst)



############## STUFF HAPPENS HERE  #############

if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://%s:%s" % (ws_host, ws_port), debugWamp = True)
   factory.protocol = SimpleClientProtocol
   connectWS(factory)
   reactor.run()
