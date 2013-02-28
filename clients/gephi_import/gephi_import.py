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
import json
import sys
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
   def updateGraph(self, msg):
      #jsonMessage = json.dumps(msg)   
      print "sending %s to %s" % (msg, topicUri)# DEBUG
      # Send the message to moirai
      self.publish("appDomain:graph" + topicId, msg)

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
      # on_message will receive the graph send an event to moirai server
      print "Connecting to Gephi" # DEBUG
      websocket_connect(gephi_address)


#################### Handle the Gephi Graph & Web Socket ####################


# Defines websocket message handler
def on_message(ws, message):
#   print message #DEBUG
   print "Message Received... "
   global timeout
   timeout = 3
#   convertedMsg = convert(message)
#   jsonMsg = json.loads(message, object_hook=ascii_encode_dict)
   jsonMsg = json.loads(message)
   convertedMsg = convert(jsonMsg)
   try:
      proto.publish("appDomain:graph" + topicId, convertedMsg)
      print "Success"
   except Exception as inst:
      print "Fail"
#      print type(inst)
#      print inst.args
      print inst

 # Defines websocket error handler
def on_error(ws, error):
    print "Gephi " + error

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

# convert unicode to ascii
# because json.loads sending out unicode and autobahn chokes on it
#def convert(input):
#    if isinstance(input, dict):
#        ret = {}
#        for stuff in input:
#            ret = convert(stuff)
#    elif isinstance(input, list):
#        ret = []
#        for i in range(len(input)):
#            ret = convert(input[i])
#    elif isinstance(input, str):
#        ret = input.encode('ascii')
#    else:
#        ret = input
#    return ret
def convert(instuff):
   if isinstance(instuff, dict):
      return dict((convert(key), convert(value)) for key, value in instuff.iteritems())
   elif isinstance(instuff, list):
      return [convert(element) for element in instuff]
   elif isinstance(input, unicode):
      return input.encode('utf-i')
   else:
      return instuff

#def ascii_encode_dict(data):
#   ascii_encode = lambda x: x.encode('ascii')
#   return dict(map(ascii_encode, pair) for pair in data.items())


########################  RUN MAIN ############################


if __name__ == '__main__':
    ##### HERES WHERE WE DO THINGS ######
    # Connect to moirai socketio websocket
    log.startLogging(sys.stdout)
    factory = WampClientFactory("ws://" + moirai_host + ":" + moirai_port, debug=True)
    factory.protocol = MyClientProtocol
    proto = factory.protocol()
    session = connectWS(factory)
    reactor.run()
    
