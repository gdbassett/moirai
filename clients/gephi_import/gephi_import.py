###############################
# Name: Gephi Import Client for Moirai
# Author: Gabriel Bassett
#
# Purpose: read a graph from gephi and store it in Moirai
# Method: import graph from gephi over websocket
#         store in networkx graph in python
#         add to neo4j using DCES format
#         
#
###############################

import websocket
import thread
import time
#import networkx as nx
import json
#import httplib
import sys
#import asyncore
#import random
#import string
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred, DeferredList
from autobahn.websocket import connectWS
from autobahn.wamp import WampClientFactory, WampClientProtocol


# Statically set WS URL
app_domain = "informationsecurityanalytics.com"
app_name = "moirai"
topicId = "1"
topicUri = "http://%s/%s/graph%s" % (app_domain, app_name, topicId)

gephi_address = "ws://localhost:8080/workspace0"
moirai_host = "localhost"
moirai_port = "9000"


# Timeout initial value (this may be a hack)
timeout = 5


#################### Handle the Moirai Web Socket ####################

class MyClientProtocol(WampClientProtocol):
   """
   Demonstrates simple Publish & Subscribe (PubSub) with Autobahn WebSockets.
   """

   # parse WS into graph format
   def updateGraph(self, message):
      jsonMessage = json.loads(message)   
      print "sending " + jsonMessage # DEBUG
      # Send the message to moirai
      self.publish(topicUri, jsonMessage)
      

   def show(self, result):
      print "SUCCESS:", result

   def logerror(self, e):
      erroruri, errodesc = e.value.args
      print "ERROR: %s ('%s')" % (erroruri, errodesc)

   def done(self, *args):
      self.sendClose()

   def onApp(self, topicUri, event):
      print app_name, topicUri, event

   def onSessionOpen(self):
      print "Session Opened"

      # Prefix the domain
      self.prefix("appDomain", "http://%s/%s/" % (app_domain, app_name)) 

      print "Subscribing to AppDomain:graph" + topicId
      self.subscribe("appDomain:graph" + topicId, self.onApp)

      print "TopicUri is %s" % topicUri


      # Connect to gephi which will send the graph
      # on_message will receive the graph send a msg to moirai
      print "Connecting to Gephi" # DEBUG
      websocket_connect(gephi_address)


#################### Handle the Gephi Graph & Web Socket ####################


def addNode(NodeMessage):
#    for i in NodeMessage:
#        G.add_node(int(i), NodeMessage[i])
#        print "node %s with attributes %s added" % (i, NodeMessage[i]) # DEBUG
    return

def addEdge(EdgeMessage):
#    for i in EdgeMessage:
#        source = int(EdgeMessage[i].pop("source"))
#        target = int(EdgeMessage[i].pop("target"))
#        EdgeMessage[i]["id"] = int(i)
#        G.add_edge(source, target, EdgeMessage[i])
#        print "edge %s with source %s, target %s, and attributes %s added" % (EdgeMessage[i]["id"], source, target, EdgeMessage[i]) # DEBUG
    return

# Defines websocket message handler
def on_message(ws, message):
#    print message #DEBUG
    global timeout
    timeout = 3
    updateGraph(message)

 # Defines websocket error handler
def on_error(ws, error):
    print error

 # Defines websocket close handler
def on_close(ws):
    print "### closed ###"

 # Defines websocket open handler
def on_open(ws):
    def run(*args):
        print "Socket open, thread started."
        global timeout
#        for i in range(3): #DEBUG
#            time.sleep(1) #DEBUG
#            ws.send("Hello %d" % i) #DEBUG
        while timeout > 0:
            timeout = timeout - 1
            time.sleep(1)
         # Add Edges
           
#        ws.sock.settimeout(5) # sets the timeout but does nothing
        print "thread terminating..."
        print "Closing Socket"
        ws.close()
#        print ws.sock.gettimeout() #DEBUG
    thread.start_new_thread(run, ())

# opens a websocket to ws_url
def websocket_connect(ws_url):
#    websocket.enableTrace(True) # DEBUG
    ws = websocket.WebSocketApp(ws_url,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()


    return ws


########################  RUN MAIN ############################


if __name__ == '__main__':
    ##### HERES WHERE WE DO THINGS ######
    # Connect to moirai socketio websocket
    log.startLogging(sys.stdout)
    factory = WampClientFactory("ws://" + moirai_host + ":" + moirai_port)
    factory.protocol = MyClientProtocol
    connectWS(factory)
    reactor.run()
