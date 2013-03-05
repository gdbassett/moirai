###############################################################################
##
##  Copyright 2011,2012 Tavendo GmbH
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


import sys
 
from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
 
from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, \
                          WampServerProtocol, \
                          exportPub, \
                          exportSub, \
                          exportRpc

import moirai

# Import py2neo to support the cypher RPC & to pass the graph to the moirai module
from py2neo import neo4j, cypher

# TODO: provide config file or command line for variables
app_domain = "informationsecurityanalytics.com"
app_name = "moirai"
webserver_directory = "."
webserver_port = 8081
ws_host = "localhost"
ws_port = "9000"
neo4j_host = "localhost"
neo4j_port = "7474"
topicIds = [1]

# Establish the connection to the neo4j database
graph_db = neo4j.GraphDatabaseService("http://" + neo4j_host + ":" + neo4j_port + "/db/data/")
 
# This handles the subscriptions and publications for the app
class MyTopicService:

   def __init__(self, allowedTopicIds):
      self.allowedTopicIds = allowedTopicIds
      print "Allowed topics are %s" % allowedTopicIds # debug


   # returns true or false  if we're going to let the client subscribe to
   #   the topic prefix (graph) and suffix (a number)
   @exportSub("graph", True)
   def subscribe(self, topicUriPrefix, topicUriSuffix):
      """
      Custom topic subscription handler.
      """
      print "client wants to subscribe to prefix %s and suffix %s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         if i in self.allowedTopicIds:
            print "Subscribing client to topic Moirai %d" % i
            return True
         else:
            print "Client not allowed to subscribe to topic Moirai %d" % i
            return False
      except:
         print "illegal topic - skipped subscription"
         return False


   @exportPub("graph", True)
   def publish(self, topicUriPrefix, topicUriSuffix, event):
      """
      Custom topic publication handler.
      """
      print "client wants to publish to %s%s" % (topicUriPrefix, topicUriSuffix)
#      print "event dir is %s" % event # DEBUG
      try:
         i = int(topicUriSuffix)
         # check that the topic is allowed (only using '1' right now)
         if i in self.allowedTopicIds:
            # Add 'and "DCES_VERSION" in event' to below to check that message
            #   is actually a DCES message, (in case other graph messase are used)
            if type(event) == dict:
               updatedEvent = {} # empty dictionary for the updated Event
               if "ae" in event: # handle add edge
                  IDs = moirai.ae_handler(graph_db,event["ae"])
                  # rewrite the event to use the DBID instead of the originID
                  updatedEvent["ae"] = {}
                  for originID in IDs:
                     updatedEvent["ae"][IDs[originID]] = event["ae"][originID]
                     # Add the origin ID to the DCES record just for reference
                     updatedEvent["ae"][IDs[originID]]["originID"] = originID
               if "an" in event: # handle add node
                  print "Adding Node" #debug
                  # Add the node to the neo4j database
                  IDs = moirai.an_handler(graph_db,event["an"])
                  # rewrite the event to use the DBID instead of the originID
                  updatedEvent["an"] = {}
                  for originID in IDs:
                     updatedEvent["an"][IDs[originID]] = event["an"][originID]
                     # Add the origin ID to the DCES record just for reference
                     updatedEvent["an"][IDs[originID]]["originID"] = originID
               if "ce" in event: # handle change edge
                  moirai.ce_handler(graph_db,event["ce"])
                  # Add the ce DCES records to the updated event
                  updatedEvent["ce"] = event["ce"]
               if "cn" in event: # handle change node
                  moirai.cn_handler(graph_db,event["cn"])
                  # Add the cn DCES records to the updated event
                  updatedEvent["cn"] = event["cn"]
               if "de" in event: # handle delete edge
                  moirai.de_handler(graph_db,event["de"])
                  # Add the de DCES records to the updated event
                  updatedEvent["de"] = event["de"]
               if "dn" in event: # handle delete node
                  moirai.dn_handler(graph_db,event["dn"])
                  # Add the dn DCES records to the updated event
                  updatedEvent["dn"] = event["dn"]
               if "re" in event: # handle replace edge
                  moirai.re_handler(graph_db,event["re"])
                  # Add the re DCES records to the updated event
                  updatedEvent["re"] = event["re"]
               if "rn" in event: # handle replace node
                  moirai.rn_handler(graph_db,event["rn"])
                  # Add the rn DCES records to the updated event
                  updatedEvent["rn"] = event["rn"]
               print "ok, publishing updated event %s" % updatedEvent
               return updatedEvent
            else:
               print "event is not dict or misses DCES Version"
               return None
         else:
            print "Topic %s not in allowed topics." % i
      except:
         print "illegal topic - skipped publication of event"
         return None


   # TODO: Make "params" optional
   # TODO: check topic list before executing
   @exportRpc
   def cypher(self, query, params):
      print "Executing query " + query # DEBUG
      resp_list, metadata = cypher.execute(graph_db, query, params) # TODO: row handler needs to be changed
      # Format the output into something serializable
      print "Results Received from query.  Formatting now." # DEBUG
      results = []
      results.append(metadata.columns)
      for i in resp_list:
         row = []
         for j in i:
            if isinstance(j, neo4j.Node) or isinstance(j, neo4j.Relationship):
               row.append({j.id:j.get_properties()})
            else:
               row.append(j)
         results.append(row)
      print "Returning Results." # DEBUG
      return results
               


# This is the actual app
class PubSubServer1(WampServerProtocol):
 
   def onSessionOpen(self):
 
      # This says run this app when the below link is requested on the WS
      ## register a single, fixed URI as PubSub topic
      self.registerForPubSub("http://" + app_domain + "/" + app_name)
 
      # This picks a few topics within the app and says what to do with them
      ## register a topic handler to control topic subscriptions/publications
      self.topicservice = MyTopicService(topicIds)
      self.registerHandlerForPubSub(self.topicservice, "http://%s/%s/" % (app_domain, app_name))

      # Register an RPC to handle Cypher requests
      self.registerForRpc(self.topicservice, "http://%s/%s/" % (app_domain, app_name))

      
 
if __name__ == '__main__':
 
   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
 
   factory = WampServerFactory("ws://" + ws_host + ":" + ws_port, debugWamp = debug)
   factory.protocol = PubSubServer1
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)
 
   webdir = File(webserver_directory)
   web = Site(webdir)
   reactor.listenTCP(webserver_port, web)
 
   reactor.run()
