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
 Used to test validation of CPTs sent from a pubsub client

 TODO:
 

 NOTES:
 

'''

### Imports ###


import sys, getopt, ConfigParser, time
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


###  Static Variables ###

config_file = "moirai.cfg"

helpMsg = 'abclienttemplate.py [options]\r\n  -h : This message\r\n  -t <topicId> : The graph topic to subscribe to.\r\n  -d <app domain> : The app domain to connect to.\r\n  -a <app name> : The name of the app to connect to.\r\n  -s <server host> : The websocket server host.\r\n  -p <server port> : The websocket server port.'


# Adds 5 nodes and links 2
event1 = {"dces_version":"0.2","an":{"A":{"label":{"description":"A Required Attribute"},"class":"attribute","start":"2013-03-14T16:57Z","cpt":{"nodeid":"A","index":[True,False],"0":[1,0]},"comment":"This attribute is required"},"B":{"label":"An Event Happens","class":"event","start":"2013-03-14T16:57Z","cpt":{"nodeid":"B","index":[True,False],"0":[1,0]},"comment":"An event happens.  This should have parents, but we're not going to bother"},"C":{"label":"resulting condition","class":"condition","start":"2013-03-14T16:57Z","cpt":{"nodeid":"C","index":["A","B",True,False],"0":[0,0,0,1],"1":[0,1,0,1],"2":[1,0,0,1],"3":[1,1,1,0]}, "comment":"Because of the Attribute and Event, this condition happens."},"D":{"label":{"description":"A previously unrequired attribute"},"class":"attribute","start":"2013-03-14T16:57Z","cpt":{"nodeid":"D","index":[True,False],"0":[1,0]},"comment":"This attribute isnt in C's CPT"},"E":{"label":"A previously unrequired Event","class":"event","start":"2013-03-14T16:57Z","cpt":{"nodeid":"E","index":[True,False],"0":[1,0]},"comment":"An event isn't in E's CPT but will be linked by an edge.  This should have parents, but we're not going to bother"}},"ae":{"1":{"source":"A","target":"C","directed":True, "relationship":"influences","start":"2013-03-14T16:57Z", "comment":"Connects attribute to condition"},"2":{"source":"B","target":"C","directed":True, "relationship":"leads to","start":"2013-03-14T16:57Z","comment":"connects event to condition"}}}

clrGraph = "START n = node(*) MATCH n-[r?]-() DELETE n,r;"

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
      idMap = {}
      print app_name, topicUri, event
      if "an" in event:
         for node in event["an"]:
            idMap[event["an"][node]["originid"]] = node

      # Adds two previously undefined edges
      # requires D, E, and C in idMap
      event2 = {"dces_version":"0.2","ae":{"4":{"source":int(idMap["D"]),"target":int(idMap["C"]),"directed":True, "relationship":"influences","start":"2013-03-14T16:57Z", "comment":"Connects attribute to condition"},"5":{"source":int(idMap["E"]),"target":int(idMap["C"]),"directed":True, "relationship":"leads to","start":"2013-03-14T16:57Z","comment":"connects event to condition"}}}
      # Only adds attribute edge.  Need to test attribute edge adding logic.
#      event2 = {"dces_version":"0.2","ae":{"4":{"source":int(idMap["D"]),"target":int(idMap["C"]),"directed":True, "relationship":"influences","start":"2013-03-14T16:57Z", "comment":"Connects attribute to condition"}}}
      # Only adds event edge.  Needed to test event edge adding logic
#      event2 = {"dces_version":"0.2","ae":{"5":{"source":int(idMap["E"]),"target":int(idMap["C"]),"directed":True, "relationship":"leads to","start":"2013-03-14T16:57Z","comment":"connects event to condition"}}}

      # Deletes the first two edges.  Requires A, B, & C in idMap
      event3 = {"dces_version":"0.2","de":{"1":{"source":int(idMap["A"]),"target":int(idMap["C"])},"2":{"source":int(idMap["B"]),"target":int(idMap["C"])}}}

      # Run Adding Edges to force CPT Updates
      print "Adding Edges %s" % event2
      self.publish("moirai:graph1", event2)

      # pause
      time.sleep(5)

      # Deleting edges to force CPT updates
      print "Deleting Edges %s" % event3
      self.publish("moirai:graph1", event3)

      # pause
      time.sleep(5)

   def onSessionOpen(self):
      print "Session Opened"

      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s/" % (app_domain, app_name))

      # subscribe to the pubsub of the graph
      print "Subscribing to moirai:graph1"
      self.subscribe("moirai:graph1", self.onApp)      

      # Clear the graph before adding to it
      print "Clearing the Graph by Cypher"
      self.call("moirai:cypher", clrGraph, params).addCallback(self.show)

      # Pause
      time.sleep(5)

      # Publish a small graph using ANs and AEs
      print "Publishing AN/AEs %s" % event1
      self.publish("moirai:graph1", event1, excludeMe=False)

      # Give the pubsub enough time to send back the event so we can get the dbIDs
      time.sleep(5)

      # quit after doing stuff
#      self.done()


### Program Execution ###


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://" + ws_host + ":" + ws_port)
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
