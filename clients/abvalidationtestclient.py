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


import sys, getopt, ConfigParser, time
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


###  Static Variables ###

config_file = "moirai.cfg"

helpMsg = 'abclienttemplate.py [options]\r\n  -h : This message\r\n  -t <topicId> : The graph topic to subscribe to.\r\n  -d <app domain> : The app domain to connect to.\r\n  -a <app name> : The name of the app to connect to.\r\n  -s <server host> : The websocket server host.\r\n  -p <server port> : The websocket server port.'

idMap = {"A":"","B":"","C":"","D":"","1":"","2":"","3":""}

event1 = {"dces_version":"0.2","ae":{"1":{"source":"D","target":"A","directed":True, "relationship":"describes","start":"2013-03-14T16:57Z"},"2":{"source":"A","target":"B","directed":True, "relationship":"leads to","start":"2013-03-14T16:57Z","comment":"I'm sure!"},"3":{"source":"B","target":"C","directed":True, "relationship":"leads to","start":"2013-03-14T16:57Z"}},"an":{"A":{"label":"haxor","class":"actor","start":"2013-03-14T16:57Z","cpt":{"nodeid":"A","index":["E",True,False],"0":[0,1],"1":[1,0]},"comment":"A youtube educated hacker"},"B":{"label":"Haxors your site","class":"event","start":"2013-03-14T16:57Z","cpt":{"nodeid":"B","index":["A",True,False],"0":[0,1],"1":[0.9,0.1]},"comment":"Uses db_autopwn"},"C":{"label":"Your sites pwnd","class":"condition","start":"2013-03-14T16:57Z","cpt":{"nodeid":"C","index":["B",True,False],"0":[0,1],"1":[1,0]}},"D":{"class":"attribute","metadata":{"skills":"leet"},"start":"2013-03-14T16:57Z","cpt":{"nodeid":"D","index":[True,False],"0":[1,0]}}}}

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
      print app_name, topicUri, event
      if "an" in event:
         for node in event["an"]:
            idMap[event["an"][node]["originid"]] = node

      event2 = {"dces_version":"0.2","re":{"2":{"source":int(idMap["A"]),"target":int(idMap["B"]),"directed":True, "relationship":"leads to","start":"2013-03-14T16:57Z","confidence":90}},"rn":{int(idMap["B"]):{"label":"Pays someone else to hack your site","class":"event","start":"2013-03-14T16:57Z","cpt":{"nodeid":"B","index":["A",True,False],"0":[0,1],"1":[0.9,0.1]},"finish":"2013-03-20T16:57Z"},}}

      event3 = {"dces_version":"0.2","cn":{int(idMap["D"]):{"label":"target has leet hacking skills"}},"ce":{"1":{"source":int(idMap["D"]),"target":int(idMap["A"]),"confidence":80}}}

      event4 = {"dces_version":"0.2","dn":{int(idMap["B"]):{}},"de":{"1":{"source":int(idMap["D"]),"target":int(idMap["A"])}}}
      
      print "AN/AE done.  Press any key to run RN/RE"
      raw_input()

      # Run RNs and REs
      print "Publishing RN/REs %s" % event2
      self.publish("moirai:graph1", event2)

      # pause
#      time.sleep(5)

      print "RN/RE done.  Press any key to run CN/CE"
      raw_input()

      # Run CNs and CEs
      print "Publishing CN/CEs %s" % event3
      self.publish("moirai:graph1", event3)

      # pause
#      time.sleep(5)

      print "CN/CE done.  Press any key to run DN/DE."
      raw_input()

      # Run DNs and DEs
      print "Publishing DN/DEs %s" % event4
      self.publish("moirai:graph1", event4, excludeMe=False)



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
