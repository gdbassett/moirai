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
 Autobahn client template

 TODO:
 

 NOTES:
 

'''

### Imports ###


import sys, getopt, ConfigParser
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


###  Static Variables ###

config_file = "moirai.cfg"

helpMsg = 'abclienttemplate.py [options]\r\n  -h : This message\r\n  -t <topicId> : The graph topic to subscribe to.\r\n  -d <app domain> : The app domain to connect to.\r\n  -a <app name> : The name of the app to connect to.\r\n  -s <server host> : The websocket server host.\r\n  -p <server port> : The websocket server port.'

# Subscribe Variables
#app_domain = "informationsecurityanalytics.com"
#app_name = "moirai"
#topicId = "1"

# Server Variables
#ws_host = "localhost"
#ws_port = "9000"

# Test Data
testDict = {'an': {'21': {'b': 0.6901961, 'g': 0.7882353, 'Degree': 4, 'Label': 'Sends phishing email asking for info to be mailed back or entered into website.', 'r': 0.4745098, 'y': -350.97687, 'x': 307.24896, 'z': 0, 'CPT': '{"nodeId":21,"index":["18",true,false],"1":[1,"1","0"],"0":[0,"0","1"]}', 'Class': 'Event', 'size': 42.4}}}
query = "START n = node(*) RETURN *;"
params = {}


### SET ENVIRONMENT ###


# Read Config File
config = ConfigParser.ConfigParser()
config.read(config_file)
topicId = config.get("Subscribe", "topicId")  
ws_host = config.get("Server", "ws_host")
ws_port = config.get("Server", "ws_port")
app_domain = config.get("Subscribe", "app_domain")
app_name = config.get("Subscribe", "app_name")

# Read Command Line Arguements
try:
   opts, args = getopt.getopt(sys.argv[1:],"ht:d:a:s:p:")
except getopt.GetoptError:
   print " Error!\r\n " + helpMsg
   sys.exit(2)
for opt, arg in opts:
   if opt == '-h':
      print helpMsg
      sys.exit()
   elif opt in ("-t"):
      topicId = arg
   elif opt in ("-d"):
      app_domain = arg
   elif opt in ("-a"):
      app_name = arg
   elif opt in ("-s"):
      ws_host = arg
   elif opt in ("-p"):
      ws_port = arg


### Class & Method Definitions ###


class MyClientProtocol(WampClientProtocol):

   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc = e.value.args
      print "ERROR: %s ('%s')" % (erroruri, errodesc)

   def done(self, *args):
      self.sendClose()

   # What to do when receiving an event from pubsub
   def onApp(self, topicUri, event):
      print app_name, topicUri, event


   def onSessionOpen(self):
      print "Session Opened"

      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s/" % (app_domain, app_name))

      # subscribe to the pubsub of the graph
      print "Subscribing to moirai:graph1"
      self.subscribe("moirai:graph1", self.onApp)

      # Example of publish to the pubsub
      self.publish("moirai:graph1", testDict)

      # Example to make a call to the Cypher RPC
      self.call("moirai:cypher", query, params).addCallback(self.show)

      # quit after doing stuff
#      self.done()


### Program Execution ###


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://" + ws_host + ":" + ws_port)
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
