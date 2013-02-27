import sys
 
from twisted.python import log
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.static import File
 
from autobahn.websocket import listenWS
from autobahn.wamp import WampServerFactory, \
                          WampServerProtocol, \
                          exportPub, \
                          exportSub

import moirai

from py2neo import cypher # needed because cypher code isn't in moirai.py

# TODO: Move a ton of the stuff to variables up here or to a config file
#         can override variable @ the command line later.
 
 
# This handles the subscriptions and publications for the app
class MyTopicService:

   def __init__(self, allowedTopicIds):
      self.allowedTopicIds = allowedTopicIds
      self.serial = 0 # TODO Remove this
      print "Allowed topics are %s" % allowedTopicIds # debug


   # returns true or false  if we're going to let the client subscribe to
   #   the topic prefix (foobar) and suffix (a number)
   @exportSub("main", True)
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


   @exportPub("main", True) #TODO: Replace Foobar w/ something more correct
   def publish(self, topicUriPrefix, topicUriSuffix, event):
      """
      Custom topic publication handler.
      """
      print "client wants to publish to %s%s" % (topicUriPrefix, topicUriSuffix)
      try:
         i = int(topicUriSuffix)
         #TODO: Add check on topicUriSuffix in allowedTopicIds
         #TODO: If event includes a DCES event, run the appropriate Moirai Handler
"""
         # check that the topic is allowed (only using '1' right now)
         if i in self.allowedTopicIds:
            # check the DCES type
            if type(event) == dict and event.has_key("DCES_TYPE") and event["DCES_TYPE"] == "graph":
               if "ae" in DCES_Message: # handle add edge
                  IDs = moirai.ae_handler(graph_db,DCES_Message["ae"])
                  # TODO: resend node to all clients
#                  socket.send_and_broadcast_channel({"action":"message", "message":json.dumps(IDs)})
               if "an" in DCES_Message: # handle add node
                  print "Adding Node" #debug
                  IDs = moirai.an_handler(graph_db,DCES_Message["an"])
                  # TODO: resend node to all clients
                  print "Sending IDs back" #debug
#                  socket.send_and_broadcast_channel({"action":"message", "message":json.dumps(IDs)}) # send back the ID Mapping
               if "ce" in DCES_Message: # handle change edge
                  moirai.ce_handler(graph_db,DCES_Message["ce"])
               if "cn" in DCES_Message: # handle change node
                  moirai.cn_handler(graph_db,DCES_Message["cn"])
               if "de" in DCES_Message: # handle delete edge
                  moirai.de_handler(graph_db,DCES_Message["de"])
               if "dn" in DCES_Message: # handle delete node
                  moirai.dn_handler(graph_db,DCES_Message["dn"])
               if "re" in DCES_Message: # handle replace edge
                  moirai.re_handler(graph_db,DCES_Message["re"])
               if "rn" in DCES_Message: # handle replace node
                  moirai.rn_handler(graph_db,DCES_Message["rn"])
"""
"""
            #TODO: Rewrite cypher as as a RDP call
            elif message["action"] == "cypher":
               print(message) #debug
               # Build a Cypher query
               query = message["message"]["query"] #"START a=node({A}) MATCH a-[:KNOWS]->b RETURN a,b"
               params = message["message"]["params"]
               node_list, metadata = cypher.execute(graph_db, query, params) # TODO: row handler needs to be changed

               results = []
               results.append(metadata.columns)
               for i in node_list:
                  row = []
                  for j in i:
                     if isinstance(j, neo4j.Node) or isinstance(j, neo4j.Relationship):
                        row.append({j.id:j.get_properties()})
                     else:
                        row.append(j)
                  results.append(row)
#               socket.send_and_broadcast_channel({"action":"message", "message":json.dumps(results)}) # send the query
"""
"""
            print "ok, published enriched event"
            return event
         else:
            print "event is not dict or misses DCES Event"
            return None
      except:
         print "illegal topic - skipped publication of event"
         return None

# This is the actual app
class PubSubServer1(WampServerProtocol):
 
   def onSessionOpen(self):
 
      # This says run this app when the below link is requested on the WS
      ## register a single, fixed URI as PubSub topic
      self.registerForPubSub("http://infosecanalytics.com/moirai")
 
      # This says run this app when the below link is requested on the WS
      ## register a URI and all URIs having the string as prefix as PubSub topic
#      self.registerForPubSub("http://example.com/event#", True) # infosecanalytics for domain & moirai for app

      # This picks a few topics within the app and says what to do with them
      ## register a topic handler to control topic subscriptions/publications
      self.topicservice = MyTopicService([1])
      self.registerHandlerForPubSub(self.topicservice, "http://infosecanalytics.com/moirai")

 
 
if __name__ == '__main__':
 
   log.startLogging(sys.stdout)
   debug = len(sys.argv) > 1 and sys.argv[1] == 'debug'
 
   factory = WampServerFactory("ws://localhost:9000", debugWamp = debug)
   factory.protocol = PubSubServer1
   factory.setProtocolOptions(allowHixie76 = True)
   listenWS(factory)
 
   webdir = File(".")
   web = Site(webdir)
   reactor.listenTCP(8080, web)
 
   reactor.run()
