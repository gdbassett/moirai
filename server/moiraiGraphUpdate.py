###############################################################################
##
##  Copyright 2011,2012,2013 Gabriel Bassett
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
# Handles the passing of graph information to Moirai
# TODO: Make EVERYTHING lower case


### INCLUDES ###

# Imported to parse the date
from dateutil import parser
import datetime

# For Neo4J integration
from py2neo import neo4j, cypher

# For json
import json


### STATIC VARIABLES ###



### Set Environment ###



### CLASS AND METHOD DEFINITIONS #### 



# add the node, return the ID from Neo4j
# returns a dictionary with key of origin ID and value of DB ID
def ae_handler(graph_db, update):
   IDs = {}
   for i in update:
      source = graph_db.get_node(update[i]["source"])
      target = graph_db.get_node(update[i]["target"])
      source_attrs = source.get_properties()
      # TODO: Pop source/target off of update?
      if "Metadata" in update[i]:
         update[i]["Metadata"] = json.dumps(update[i]["Metadata"])
      if "Class" in source_attrs and source_attrs["Class"] == "Attribute":
         relationship = "describes" # not sure the double list reference is correct
      else:
         relationship = "leads to"
      edge = graph_db.get_or_create_relationships((source, relationship, target, update[i]))
      IDs[i] = edge[0].id
   return IDs


# add the node, return the ID from Neo4j
# returns a dictionary with key of origin ID and value of DB ID
def an_handler(graph_db, update):
   print "Starting to add the node" # debug
   IDs = {}
   for i in update:
      # TODO: Make sure the node doesn't already exist
      if "Metadata" in update[i]:
         update[i]["Metadata"] = json.dumps(update[i]["Metadata"])
      #TODO Pop ID key off of update?
      n = graph_db.create(update[i]) # ignores ID passed in
      IDs[i] = n[0].id
   print "Done adding the node" # debug
   return IDs


# get the edge by id then update it with the given attributes
# (if source/destination changes, get it's properties, delete the edge,
# update the properties, delete, replace, and return the ID)
# TODO: DOUBLE CHECK
def ce_handler(graph_db, update):
   for i in update:
      query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r"
      params = {"A": update[i]["source"], "B": update[i]["target"]}
      edge, meta = cypher.execute(graph_db, query, params)
      if "Metadata" in update[i]:
         update[i]["Metadata"] = json.dumps(update[i]["Metadata"])
      edge[0][0].update_properties(update[i])
#      eproperties = edge.get_properties()
#      edge.setproperties(dict(eproperties.items() + update[i].items()))


# get the node by id and update it with the given attributes.  Return the ID
#TODO DOUBLE CHECK
def cn_handler(graph_db, update):
   for i in update:
      node = graph_db.get_node(i)
      if "metadata" in update[i]:
         update[i]["metadata"] = json.dumps(update[i]["metadata"])
      node.update_properties(update[i])
#      nproperties = node.getproperties()
#      node.set_properties(dict(nproperties.items() + update[i].items()))



# get the edge by id and delete it, return ID or false
#TODO DOUBLE CHECK
def de_handler(graph_db, update):
   for i in update:
      query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r"
      params = {"A": update[i]["source"], "B": update[i]["target"]}
      edge, meta = cypher.execute(graph_db, query, params)
      print edge[0][0] # DEBUG
      edge[0][0].delete()


# get the node by id and delete it, return ID or false
# TODO: DOUBLE CHECK
def dn_handler(graph_db, update):
   for i in update:
      node = graph_db.get_node(i)
      parent_edges = node.get_relationships(0)
      child_edges = node.get_relationships(1)
      for edge in parent_edges:
         edge.delete()
      for edge in child_edges:
         edge.delete()
      node.delete()


# get the edge by id, delete it, and add the given edge.
# Return the new edge ID
def re_handler(graph_db, update):
   for i in update:
      query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r"
      params = {"A": update[i]["source"], "B": update[i]["target"]}
      edge, meta = cypher.execute(graph_db, query, params)
      if "Metadata" in update[i]:
         update[i]["Metadata"] = json.dumps(update[i]["Metadata"])
      edge[0][0].set_properties(update[i])


# get the node by id, delete it, and add the given node.
# REturn the new node ID
def rn_handler(graph_db, update):
   for i in update:
      node = graph_db.get_node(i)
      if "Metadata" in update[i]:
         update[i]["Metadata"] = json.dumps(update[i]["Metadata"])
      node.set_properties(update[i])

# TAKES: the graph and event
# DOES: adds the event to the graph
# RETURNS: the event as in the graph (replaced IDs)
def addDcesEvent(graph_db, event):
   # Add 'and "DCES_VERSION" in event' to below to check that message
   #   is actually a DCES message, (in case other graph messase are used)
   updatedEvent = {} # empty dictionary for the updated Event
   if "ae" in event: # handle add edge
      IDs = ae_handler(graph_db,event["ae"])
      # rewrite the event to use the DBID instead of the originID
      updatedEvent["ae"] = {}
      for originID in IDs:
         updatedEvent["ae"][IDs[originID]] = event["ae"][originID]
         # Add the origin ID to the DCES record just for reference
         updatedEvent["ae"][IDs[originID]]["originID"] = originID
   if "an" in event: # handle add node
      print "Adding Node" #debug
      # Add the node to the neo4j database
      IDs = an_handler(graph_db,event["an"])
      # rewrite the event to use the DBID instead of the originID
      updatedEvent["an"] = {}
      for originID in IDs:
         updatedEvent["an"][IDs[originID]] = event["an"][originID]
         # Add the origin ID to the DCES record just for reference
         updatedEvent["an"][IDs[originID]]["originID"] = originID
   if "ce" in event: # handle change edge
      ce_handler(graph_db,event["ce"])
      # Add the ce DCES records to the updated event
      updatedEvent["ce"] = event["ce"]
   if "cn" in event: # handle change node
      cn_handler(graph_db,event["cn"])
      # Add the cn DCES records to the updated event
      updatedEvent["cn"] = event["cn"]
   if "de" in event: # handle delete edge
      de_handler(graph_db,event["de"])
      # Add the de DCES records to the updated event
      updatedEvent["de"] = event["de"]
   if "dn" in event: # handle delete node
      dn_handler(graph_db,event["dn"])
      # Add the dn DCES records to the updated event
      updatedEvent["dn"] = event["dn"]
   if "re" in event: # handle replace edge
      re_handler(graph_db,event["re"])
      # Add the re DCES records to the updated event
      updatedEvent["re"] = event["re"]
   if "rn" in event: # handle replace node
      moirai.rn_handler(graph_db,event["rn"])
      # Add the rn DCES records to the updated event
      updatedEvent["rn"] = event["rn"]
   print "ok, publishing updated event %s" % updatedEvent
   return updatedEvent

# TAKES: A single node property dictionary
# DOES: Validates the event
# RETURNS: event if valid and raises ValueError if invalid
def validateNode(event):
   # check event for required property 'class'
   if "class" not in event:
      raise ValueError("event missing required class property")
   # check class for required types
   if event["class"] not in ["event", "attribute", "condition"]:
      raise ValueError("class property is not allowed types of event, attribute, condition")
   # events and conditions need to have labels
   if event["class"] in ["event"], "condition"]:
      if "label" not in event:
         raise ValueError("event or condition clas node missing label property")
   # attributes need to have metadata
   else:
      if "metadata" not in event:
         raise ValueError("no metadata property in attribute event")
      else:
         # metadata needs to be a dictionary string
         if type(event["metadata"]) == dict:
            pass
         # try and parse the metadata, if we can't return false
         else:
            try:
               event["metadata"] = json.loads(event["metadata"])
            except:
               raise ValueError("metadata property not parsable")
         # pull one type:value pair out of metadata, convert to string, & save back to metadata
         for key in event["metadata"]:
            tmp = {}
            tmp[key] = event["metadat"][key]
            event["metadata"] = json.loads(tmp) 
            # end after 1.  We're only keeping 1 pieces of metadata
            break      
   # check event for require property 'cpt'
   if "cpt" not in event:
      raise ValueError('No cpt property')
   # check event for required property 'start'
   elif "start" not in event:
      raise ValueError('No start property')
   # Either parse the start string to a valid date time or return the current date at midnight
   dt = dateutil.parse(event["start"])
   # Parse back to ISO 8601 string
   event["start"] = dt.strftime("%Y-%m-%d %H:%M:%S %z")
   # If finish exists, make sure it's a time
   if "finish" in event:
      # Either parse the start string to a valid date time or return the current date at midnight
      dt = dateutil.parse(event["finish"])
      # Parse back to ISO 8601 string
      event["finish"] = dt.strftime("%Y-%m-%d %H:%M:%S %z")
   if "comment" in event:
      try:
         event["confidence"] = str(event["confidence"])
      except:
         raise ValueError("comment could not be parsed into string")
   return event


# TAKES: An edge event
# DOES: Validates the event
# RETURNS: event if validated or ValueError if not
def validateEdge(event):
   # Check for required source property
   if "source" not in event:
      raise ValueError("No source property in edge")
   # Check for required target property
   if "target" not in event:
      raise ValueError("No target property in edge")
   # Check for required relationship property
   if "relationship" not in event:
      raise ValueError("No relationship property in edge")
   if event["relationship"] not in ["describes", "leads to"]:
      raise ValueError("Relationship not one of the two required values")
   if "directed" in event:
      if event["directed"] != True:
         raise ValueError("Edge is explicitly undirected.")
   else:
      event["directed"] = True
   if "confidence" in event:
      try:
         event["confidence"] = int(event["confidence"])
      except:
         raise ValueError("Confidence cannot be parsed to int")
      if (event["confidence"] > 100) or (event["confidence"] < 0):
         raise ValueError("Confidence value is out of range 0-100")
   if "comment" in event:
      try:
         event["confidence"] = str(event["confidence"])
      except:
         raise ValueError("comment could not be parsed into string")
   return event
