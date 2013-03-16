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


### INCLUDES ###

# Imported to parse the start and finish properties
from dateutil import parser
import datetime

# For Neo4J integration
from py2neo import neo4j, cypher

# For json
import json

# for logging failed graph adds
import logging


### STATIC VARIABLES ###



### Set Environment ###



### CLASS AND METHOD DEFINITIONS #### 


# TAKES: A py2neo graph object and an "ae" dictionary
# DOES: Validates the edge (maybe sprucing up the properties)
# DOES: add the edge
# RETURNS: a dictionary with key of origin ID and value of DB ID
def ae_handler(graph_db, event):
   IDs = {}
   for edge in event:
      logging.info("Adding Edge %s" % edge)
      # Ensure the edge has the required properties
      if validateEdge(event[edge]):
         try:
            # Ensure that the properties have the correct values
            event[edge] = validateEdgeProperties(event[edge])
            # Get the source and target edges
            source = graph_db.get_node(event[edge]["source"])
            target = graph_db.get_node(event[edge]["target"])
            source_attrs = source.get_properties()
            # Not strictly necessary, but we'll set the relationship just to make sure
            if "class" in source_attrs and source_attrs["class"] == "attribute":
               relationship = "describes" 
            else:
               relationship = "leads to"
            # Create the actual edge
            e = graph_db.get_or_create_relationships((source, relationship, target, event[edge]))
            IDs[edge] = e[0].id
         except:
            logging.error("Edge %s properties did not validate and will not be added") % edge
      else:
         logging.error("Edge %s property values did not validate and will not be added") % edge
   return IDs


# TAKES: A py2neo graph object and an "an" dictionary
# DOES: Validates the node (maybe sprucing up the properties)
# DOES: add the node
# RETURNS: a dictionary with key of origin ID and value of DB ID
def an_handler(graph_db, event):
   print "Starting to add the node" # debug
   IDs = {}
   for node in event:
      logging.info("Adding Node %s" % node) #debug
      # Make sure the node has the correct properties
      if validateNode(event[node]):
         try:
            # Make sure the properties have appropriate values
            event[node] = validateEdgeProperties(event[node])
            # TODO: Compare the node to nodes already in the graph and combine it if they already exist
            n = graph_db.create(event[node]) # ignores ID passed in
            IDs[node] = n[0].id
         except:
            logging.error("Node %s properties did not validate and will not be added") % node
      else:
         logging.error("Node %s property values did not validate and will not be added") % node
#   print "Done adding the node" # debug
   return IDs


# TAKES: A py2neo graph object and an "ce" dictionary
# DOES: Validates the edge (maybe sprucing up the properties)
# DOES: looks the edge up by source/target and adds the supplied properties dictionary
# RETURNS: nothing
def ce_handler(graph_db, event):
   query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r;"
   for edge in event:
      logging.info("Changing Edge %s" % edge) #debug
      # Make sure the edge has a source and target
      if ("source" not in event[edge]) and ("target" not in event[edge]):
         try:
            # Ensure that the properties have the correct values
            event[edge] = validateEdgeProperties(event[edge])
            # Set the params for the query to get the current edge
            params = {"A": event[edge]["source"], "B": event[edge]["target"]}
            # Retrieve the current edge
            e, meta = cypher.execute(graph_db, query, params)
            # Set the first edge in the list of current edges to the new properties
            e[0][0].update_properties(event[edge])
         except:
            logging.error("Edge %s properties did not validate and will not be added") % edge
      else:
         logging.error("Edge %s property values did not validate and will not be added") % edge


# TAKES: A py2neo graph object and an "cn" dictionary
# DOES: Validates the node (maybe sprucing up the properties)
# DOES: looks the edge up by node id and adds the supplied properties dictionary
# RETURNS: nothing
def cn_handler(graph_db, event):
   for node in event:
      logging.info("CHanging Node %s" % node) #debug
      try:
         # Make sure the properties have appropriate values
         event[node] = validateEdgeProperties(event[node])
         # Find the current node
         n = graph_db.get_node(node)
         # Update the properties
         n.update_properties(event[node])
      except:
         logging.error("Node %s properties did not validate and will not be added") % node



# TAKES: A py2neo graph object and a de event dictionary
# DOES: Identifies the edge by source/target and deletes it
# RETURNS: Nothing
def de_handler(graph_db, event):
   # Set the query to find the edge
   query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r;"
   for edge in event:
      logging.info("Deleting edge %s" % edge) #debug
      # Make sure the edge has a source and target
      if ("source" not in event[edge]) and ("target" not in event[edge]):
         params = {"A": event[edge]["source"], "B": event[edge]["target"]}
         e, meta = cypher.execute(graph_db, query, params)
         logging.info("Deleting edge %s" % e[0][0) # DEBUG
         e[0][0].delete()
      else:
         logging.error("Edge Delete missing source/target necessary to delete it.")


# TAKES: A py2neo graph object and a dn event dictionary
# DOES: Identifies the node by id and deletes it
# DOES: Deletes edges attached to the node
# RETURNS: Nothing
def dn_handler(graph_db, event):
   for node in event:
      logging.info("Deleting Node %s" % node) #debug
      # Find the node and it's edges
      n = graph_db.get_node(node)
      parent_edges = n.get_relationships(0)
      child_edges = n.get_relationships(1)
      # Delete the edges
      for edge in parent_edges:
         edge.delete()
      for edge in child_edges:
         edge.delete()
      # Delete the node
      n.delete()


# TAKES: A py2neo graph object and a re event dictionary
# DOES: Identifies the edge by source/target and replaces it's properties
# RETURNS: Nothing
def re_handler(graph_db, event):
   query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r;"
   for edge in event:
      logging.info("Replacing Edge %s" % edge)
      # Ensure the edge has the required properties
      if validateEdge(event[edge]):
         try:
            # Ensure that the properties have the correct values
            event[edge] = validateEdgeProperties(event[edge])                      
            params = {"A": event[edge]["source"], "B": event[edge]["target"]}
            # Get the edge
            e, meta = cypher.execute(graph_db, query, params)
            # Replace it's properties
            e[0][0].set_properties(event[edge])
         except:
            logging.error("Edge %s properties did not validate and will not be added") % edge
      else:
         logging.error("Edge %s property values did not validate and will not be added") % edge


# TAKES: A py2neo graph object and a rn event dictionary
# DOES: Identifies the node by id and replaces it's properties
# RETURNS: Nothing
def rn_handler(graph_db, event):
   for node in event:
      logging.info("Replace Node %s" % node) #debug
      # Make sure the node has the correct properties
      if validateNode(event[node]):
         try:
            # Make sure the properties have appropriate values
            event[node] = validateEdgeProperties(event[node])
            # Get the node, replace it's properties
            n = graph_db.get_node(edge)
            n.set_properties(event[edge])
         except:
            logging.error("Node %s properties did not validate and will not be added") % node
      else:
         logging.error("Node %s property values did not validate and will not be added") % node


# TAKES: A node property dictionary
# DOES: Validates that node has required properties
# RETURNS: True if validated, False if properties are missing
def validateNode(properties):
   # check event for required property 'class'
   if "class" not in properties:
#      raise ValueError("event missing required class property")
      return False
   # events and conditions need to have labels
   if properties["class"] in ["event", "condition"]:
      if "label" not in properties:
#         raise ValueError("event or condition clas node missing label property")
         return False
   # attributes need to have metadata
   elsif properties["class"] is "attribute":
      if "metadata" not in properties:
#         raise ValueError("no metadata property in attribute event")   
         return False
   # check event for require property 'cpt'
   if "cpt" not in properties:
#      raise ValueError('No cpt property')
      return False
   # check event for required property 'start'
   elif "start" not in properties:
#      raise ValueError('No start property')
      return False
   return True

     
# TAKES: A node event property dictionary
# DOES: Validates the event properties
# RETURNS: event property dictionary if validated or ValueError if not
def validateNodeProperties(properties):
   # check class for required types
    if "class" in properties:
        if properties["class"] not in ["event", "attribute", "condition"]:
              raise ValueError("class property is not allowed types of event, attribute, condition")
    if "metadata" in properties:
        # metadata needs to be a dictionary string
        if type(event["metadata"]) == dict:
           pass
        # try and parse the metadata, if we can't return false
        else:
           try:
              properties["metadata"] = json.loads(properties["metadata"])
           except:
              raise ValueError("metadata property not parsable")
        # pull one type:value pair out of metadata, convert to string, & save back to metadata
        for key in properties["metadata"]:
           tmp = {}
           tmp[key] = properties["metadat"][key]
           properties["metadata"] = json.loads(tmp) 
           # end after 1.  We're only keeping 1 pieces of metadata
           break      
   # check event for required property 'start'
   if "start" in properties:
       dt = dateutil.parse(properties["start"])
       # Parse back to ISO 8601 string
       properties["start"] = dt.strftime("%Y-%m-%d %H:%M:%S %z")
       # If finish exists, make sure it's a time
   if "finish" in properties:
      # Either parse the start string to a valid date time or return the current date at midnight
      dt = dateutil.parse(properties["finish"])
      # Parse back to ISO 8601 string
      event["finish"] = dt.strftime("%Y-%m-%d %H:%M:%S %z")
   if "comment" in properties:
      try:
         properties["confidence"] = str(event["confidence"])
      except:
         raise ValueError("comment could not be parsed into string")
   return properties


# TAKES: An edge property dictionary
# DOES: Validates that node has required properties
# RETURNS: True if validated, False if properties are missing
def validateEdge(properties):
   # Check for required source property
   if "source" not in properties:
#      raise ValueError("No source property in edge")
      return False
   # Check for required target property
   if "target" not in properties:
#      raise ValueError("No target property in edge")
      return False
   if "relationship" not in properties:
#      raise ValueError("No relationship property in edge")
      return False
   return True


# TAKES: An edge event property dictionary
# DOES: Validates the event properties
# RETURNS: event property dictionary if validated or ValueError if not
def validateEdgeProperties(properties):
   # Check for required relationship property
   if properties["relationship"] not in ["describes", "leads to"]:
      raise ValueError("Relationship not one of the two required values")
   if "directed" in properties:
      if properties["directed"] != True:
         raise ValueError("Edge is explicitly undirected.")
   else:
      properties["directed"] = True
   if "confidence" in properties:
      try:
         properties["confidence"] = int(properties["confidence"])
      except:
         raise ValueError("Confidence cannot be parsed to int")
      if (properties["confidence"] > 100) or (properties["confidence"] < 0):
         raise ValueError("Confidence value is out of range 0-100")
   if "comment" in properties:
      try:
         properties["confidence"] = str(event["confidence"])
      except:
         raise ValueError("comment could not be parsed into string")
   return properties


# TAKES: the graph and event
# DOES: adds the event to the graph
# RETURNS: the event as in the graph (replaced IDs)
# NOTE: Any nodes or edges that fail to validate will not be added and an error logged, but processing will continue
def addDcesEvent(graph_db, event):
   # Add 'and "DCES_VERSION" in event' to below to check that message
   #   is actually a DCES message, (in case other graph messase are used)
   updatedEvent = {} # empty dictionary for the updated Event
   if "ae" in event: # handle add edge
      # Add the edge tot he neo4j database
      IDs = ae_handler(graph_db,event["ae"])
      # rewrite the event to use the DBID instead of the originID
      updatedEvent["ae"] = {}
      for originID in IDs:
         updatedEvent["ae"][IDs[originID]] = event["ae"][originID]
         # Add the origin ID to the DCES record just for reference
         updatedEvent["ae"][IDs[originID]]["originID"] = originID
   if "an" in event: # handle add node
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
