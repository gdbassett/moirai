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

### Imports ###


import sys, getopt
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol
import ConfigParser


###  Static Variables ###

config_file = "moirai.cfg"

# Subscribe Variables
app_domain = "informationsecurityanalytics.com"
app_name = "moirai"
topicId = "1"

# Server Variables
ws_host = "localhost"
ws_port = "9000"

# Test Data
testDict = {'an': {'21': {'b': 0.6901961, 'g': 0.7882353, 'Degree': 4, 'Label': 'Sends phishing email asking for info to be mailed back or entered into website.', 'r': 0.4745098, 'y': -350.97687, 'x': 307.24896, 'z': 0, 'CPT': '{"nodeId":21,"index":["18",true,false],"1":[1,"1","0"],"0":[0,"0","1"]}', 'Class': 'Event', 'size': 42.4}}}
query = "START n = node(*) RETURN *;"
params = {}

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
   opts, args = getopt.getopt(sys.argv[1:],"ht:d:a:h:p:")
except getopt.GetoptError:
   print 'abclienttemplate.py -h -t <topicId> -d <app domain> -a <app name> -h <server Host> -p <server port>'
   sys.exit(2)
for opt, arg in opts:
   if opt == '-h':
      print 'abclienttemplate.py [options]'
      print '-h : This message'
      print '-t <topicId> : The graph topic to subscribe to.'
      print '-d <app domain> : The app domain to connect to.'
      print '-a <app name> : The name of the app to connect to.'
      print '-h <server host> : The websocket server host.'
      print '-p <server port> : The websocket server port.'
      sys.exit()
   elif opt in ("-t"):
      topicId = arg
   elif opt in ("-d"):
      app_domain = arg
   elif opt in ("-a"):
      app_name = arg
   elif opt in ("-h"):
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
