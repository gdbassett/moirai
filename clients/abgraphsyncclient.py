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


import sys, getopt, ConfigParser
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol
import networkx as nx


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
   opts, args = getopt.getopt(sys.argv[1:],"ht:d:a:h:p:")
except getopt.GetoptError:
   print helpMsg
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

# Create the empty graph to populate
G = nx.Graph()


### Class & Method Definitions ###


class MyClientProtocol(WampClientProtocol):

#   # return function for cypher call to nodes.  Ensures nodes are processed before edges
#   # TODO: This is stupid.  use the defered call function instead.
#   def nodesFirst(self, result):
#      self.show(result)
#      query2 = "START n=node(*) MATCH n-[r]->m RETURN r, ID(n), ID(m);"
#      params = {}
#      self.call("moirai:cypher", query2, params).addCallback(self.show)
   
   # Takes the entire graph as output from a cypher query
   # Parses the cypher output and adds it to the graph G
   def loadGraph(self, result):
      print result # DEBUG
      # Nodes being returned
      if result[0][0] == "n":
         # For each node
         # Node will be a dictionary w/ a key of the DBID and value of a dict of properties
         for i in range(1, len(result)):
#         for node in result[1]:
            for id in result[i]:
               G.add_node(id, result[i][id])
      # Edges being returned
      elif result[0][0] == "r":
         print result # DEBUG
         # for Each edge
         for i in range(1, len(result)):
            for id in result[i][0]:
               result[i][0][id]["id"] = int(id)
               source = int(result[i][1])
               target = int(result[i][2])
               G.add_edge(source, target, result[i][0][id])
         
      
   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc = e.value.args
      print "ERROR: %s ('%s')" % (erroruri, errodesc)

   def done(self, *args):
      self.sendClose()

   # Test to see if the graph is there
   def testGraph(self, *args):
      print "Nodes are: %s" % G.nodes()
      print "Edges are: %s" % G.edges()
      

   # TODO:
   # Receives an update to the graph
   # Parses the updated and updates the networkx graph G
   def updateGraph(self, topicUri, event):
      # TODO: First check if the node/edge exists (for updates)
      #   and if source/target exist for edge creates
      #   If necessary node/edge doesn't exist, sleep method a bit
      pass


   def onSessionOpen(self):
      print "Session Opened"

      # Set the App Prefix
      self.prefix("moirai", "http://%s/%s/" % (app_domain, app_name))

      # Retrieve the graph nodes and call self.buildGraph and
      #   a second cypher to retrieve the edges
      query = "START n=node(*) RETURN n;"
      query2 = "START n=node(*) MATCH n-[r]->m RETURN r, ID(n), ID(m);"
      params = {}
      d1 = self.call("moirai:cypher", query, params).addCallback(self.loadGraph)
      d2 = self.call("moirai:cypher", query2, params).addCallback(self.loadGraph)
      # Don't call the edges until the nodes are added
      DeferredList([d1, d2]).addCallback(self.testGraph)

      # After retrieving the current state, subscribe to the pubsub of the graph
      # Nodes and edges may still be being added when this happens.  updateGraph()
      #   needs to handle this.
      print "Subscribing to moirai:graph1"
      self.subscribe("moirai:graph1", self.updateGraph)



### Program Execution ###


if __name__ == '__main__':

   log.startLogging(sys.stdout)
   factory = WampClientFactory("ws://" + ws_host + ":" + ws_port)
   factory.protocol = MyClientProtocol
   connectWS(factory)
   reactor.run()
