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

# Import sets for when we want a list of uniques
from sets import Set

### STATIC VARIABLES ###



### Set Environment ###

# Hack to enable logging
logging.basicConfig(filename="/tmp/moirai.log", filemode='w', level=logging.DEBUG)

### CLASS AND METHOD DEFINITIONS #### 


# TAKES: A py2neo graph object and an "ae" dictionary
# DOES: Validates the edge (maybe sprucing up the properties)
# DOES: add the edge
# RETURNS: an updated "ae" dictionary with the originid added as a property
def ae_handler(graph_db, event):
   updatedAE = {}
   for edge in event:
      logging.info("Adding Edge %s" % edge)
      # Ensure the edge has the required properties
      if validateEdge(event[edge]):
         try:
            # Ensure that the properties have the correct values
            event[edge] = validateEdgeProperties(event[edge])
#            logging.debug("Event source: %s, target: %s" % (event[edge]["source"], event[edge]["target"]))
            # Get the source and target edges
            source = graph_db.get_node(event[edge]["source"])
            target = graph_db.get_node(event[edge]["target"])
            source_attrs = source.get_properties()
            target_attrs = target.get_properties()
            # Not strictly necessary, but we'll set the relationship if we can, otherwise 
            if "class" in source_attrs and "class" in target_attrs:
               if target_attrs["class"] in ["actor", "event", "condition"]:
                  if source_attrs["class"] is "attribute":
                     relationship = "influences"
                  elif source_attrs["class"] in ["actor", "event", "condition"]:
                     relationship = "leads to"
                  else:
                     relationship = event[edge]["relationship"]
               elif target_attrs["class"] is "attribute":
                  relationship = "described by"
               else:
                  relationship = event[edge]["relationship"]
#            logging.debug("Source: %s, Target: %s") % (source.id, target.id) # Debug
            # Create the actual edge
            e = graph_db.get_or_create_relationships((source, relationship, target, event[edge]))
#            logging.debug(e)
            # Store the updated edges to return
            updatedAE[e[0].id] = event[edge]
            updatedAE[e[0].id]["originid"] = edge
         except Exception as inst:
            logging.error(inst)
            logging.error("Edge %s properties did not validate and will not be added" % edge)
      else:
         logging.error("Edge %s does not have the correct properties and will not be added" % edge)
   return updatedAE


# TAKES: A py2neo graph object and an "an" dictionary
# DOES: Validates the node (maybe sprucing up the properties)
# DOES: add the node
# RETURNS: An updated "an" dictionary
def an_handler(graph_db, event):
   print "Starting to add the node" # debug
   updatedAN = {}
   for node in event:
      logging.info("Adding Node %s" % node) #debug
      # Make sure the node has the correct properties
      if validateNode(event[node]):
         try:
            # Make sure the properties have appropriate values
            event[node] = validateNodeProperties(event[node])
            # Add the originid to the event before saving it to the db
            event[node]["originid"] = node
            # TODO: Compare the node to nodes already in the graph and combine it if they already exist
            n = graph_db.create(event[node]) # ignores ID passed in
            # add the node to the AN dictionary and add the originid as a property
            updatedAN[n[0].id] = event[node]
         except Exception as inst:
            logging.error(inst)
            logging.error("Node %s properties did not validate and will not be added" % node)
      else:
         logging.error("Node %s didn't have the required properties and will not be added" % node)
#   print "Done adding the node" # debug
   return updatedAN


# TAKES: A py2neo graph object and an "ce" dictionary
# DOES: Validates the edge (maybe sprucing up the properties)
# DOES: looks the edge up by source/target and adds the supplied properties dictionary
# RETURNS: Updated "ce" dictionary
def ce_handler(graph_db, event):
   query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r;"
   updatedCE = {}
   for edge in event:
      logging.info("Changing Edge %s" % edge) #debug
      # Make sure the edge has a source and target
      if ("source" in event[edge]) and ("target" in event[edge]):
         try:
            # Ensure that the properties have the correct values
            event[edge] = validateEdgeProperties(event[edge])
            # Set the params for the query to get the current edge
            params = {"A": event[edge]["source"], "B": event[edge]["target"]}
            # Retrieve the current edge
            e, meta = cypher.execute(graph_db, query, params)
            # Set the first edge in the list of current edges to the new properties
            e[0][0].update_properties(event[edge])
            # Store the updated edges to return
            updatedCE[e[0][0].id] = event[edge]
            updatedCE[e[0][0].id]["originid"] = edge
         except Exception as inst:
            logging.error(inst)
            logging.error("Edge %s properties did not validate and will not be added" % edge)
      else:
         logging.error("Edge %s property values did not validate and will not be added" % edge)
   return updatedCE


# TAKES: A py2neo graph object and an "cn" dictionary
# DOES: Validates the node (maybe sprucing up the properties)
# DOES: looks the edge up by node id and adds the supplied properties dictionary
# RETURNS: nothing
def cn_handler(graph_db, event):
   updatedCN = {}
   for node in event:
      logging.info("Changing Node %s" % node) #debug
      try:
         # Make sure the properties have appropriate values
         event[node] = validateNodeProperties(event[node])
         # Find the current node
         n = graph_db.get_node(node)
         logging.debug(n)
         # Update the properties
         n.update_properties(event[node])
         # add the node to the AN dictionary and add the originid as a property
         updatedCN[n.id] = event[node]
         updatedCN[n.id]["originid"] = node
      except Exception as inst:
         logging.error(inst)
         logging.error("Node %s properties did not validate and will not be added" % node)
   return updatedCN



# TAKES: A py2neo graph object and a de event dictionary
# DOES: Identifies the edge by source/target and deletes it
# RETURNS: An updated de dictionary
def de_handler(graph_db, event):
   updatedDE = {}
   # Set the query to find the edge
   query = "START a=node({A}), b=node({B}) MATCH a-[r]->b RETURN r;"
   for edge in event:
      logging.info("Deleting edge %s" % edge) #debug
      # Make sure the edge has a source and target
      if ("source" in event[edge]) and ("target" in event[edge]):
         params = {"A": event[edge]["source"], "B": event[edge]["target"]}
         e, meta = cypher.execute(graph_db, query, params)
         logging.debug("e is %s" % e)
         if e != []:
            # populate the updated de dictionary.
            updatedDE[e[0][0].id] = event[edge]
            updatedDE[e[0][0].id]["originid"] = edge
            logging.info("Deleting edge %s" % e[0][0].id) # DEBUG
            # delete the edge
            e[0][0].delete()
         else:
            logging.info("Edge %s does not exist to delete." % edge)    
      else:
         logging.error("Edge Delete missing source/target necessary to delete it.")
   return updatedDE

# TAKES: A py2neo graph object and a dn event dictionary
# DOES: Identifies the node by id and deletes it
# DOES: Deletes edges attached to the node
# RETURNS: An updated dictionary with both a DN and DE dictionary
def dn_handler(graph_db, event):
   updatedDN = {}
   updatedDE = {}
   for node in event:
      logging.info("Deleting Node %s" % node) #debug
      # Find the node and it's edges
      n = graph_db.get_node(node)
      # Gets relationships in both directions
      edges = n.get_relationships(0)
      # Delete the edges
      for edge in edges:
         logging.info("Deleting Edge %s" % edge)
         updatedDE[edge.id] = edge.get_properties()
         edge.delete()
      logging.debug("Done deleting edges of %s" % n.id)
      # Update the DN dictionary
      updatedDN[n.id] = event[node]
      updatedDN[n.id]["originid"] = node
      # Delete the node
      n.delete()
   return {"dn":updatedDN, "de":updatedDE}


# TAKES: A py2neo graph object and a re event dictionary
# DOES: Identifies the edge by source/target and replaces it's properties
# RETURNS: An updated "re" dictionary
def re_handler(graph_db, event):
   updatedRE = {}
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
            # populate the updated de dictionary.
            updatedRE[e[0][0].id] = event[edge]
            updatedRE[e[0][0].id]["originid"] = edge
         except Exception as inst:
            logging.error(inst)
            logging.error("Edge %s properties did not validate and will not be added" % edge)
      else:
         logging.error("Edge %s property values did not validate and will not be added" % edge)
   return updatedRE


# TAKES: A py2neo graph object and a rn event dictionary
# DOES: Identifies the node by id and replaces it's properties
# RETURNS: Nothing
def rn_handler(graph_db, event):
   updatedRN = {}
   for node in event:
      logging.info("Replace Node %s" % node) #debug
      # Make sure the node has the correct properties
      if validateNode(event[node]):
         try:
            # Make sure the properties have appropriate values
            event[node] = validateNodeProperties(event[node])
            # Get the node, replace it's properties
            n = graph_db.get_node(node)
            n.set_properties(event[node])
            # Update the DN dictionary
            updatedRN[n.id] = event[node]
            updatedRN[n.id]["originid"] = node
         except Exception as inst:
            logging.error(inst)
            logging.error("Node %s properties did not validate and will not be added" % node)
      else:
         logging.error("Node %s property values did not validate and will not be added" % node)
   return updatedRN


# TAKES: A node property dictionary
# DOES: Validates that node has required properties
# RETURNS: True if validated, False if properties are missing
def validateNode(properties):
   # check event for required property 'class'
   if "class" not in properties:
#      raise ValueError("event missing required class property")
      return False
   # events and conditions need to have labels
   if properties["class"] in ["actor", "event", "condition"]:
      if "label" not in properties:
#         raise ValueError("event or condition clas node missing label property")
         return False
   # attributes need to have metadata
   elif properties["class"] is "attribute":
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
      if properties["class"] not in ["actor", "event", "attribute", "condition"]:
         raise ValueError("class property is not allowed types of event, attribute, condition")
   if "metadata" in properties:
 #     logging.debug(type(properties["metadata"]))
      # metadata needs to be a dictionary string
      if type(properties["metadata"]) is not dict:
         try:
            properties["metadata"] = json.loads(properties["metadata"])
         except:
            logger.error("metadata of type %s not parsable" % type(properties["metadata"]))
            raise ValueError("metadata property not parsable")
      # pull one type:value pair out of metadata, convert to string, & save back to metadata
      for key in properties["metadata"]:
         tmp = {}
         tmp[key] = properties["metadata"][key]
      properties["metadata"] = json.dumps(tmp)
   # check event for required property 'start'
   if "start" in properties:
       dt = parser.parse(properties["start"])
       # Parse back to ISO 8601 string
       properties["start"] = dt.strftime("%Y-%m-%d %H:%M:%S %z")
       # If finish exists, make sure it's a time
   if "finish" in properties:
      # Either parse the start string to a valid date time or return the current date at midnight
      dt = parser.parse(properties["finish"])
      # Parse back to ISO 8601 string
      properties["finish"] = dt.strftime("%Y-%m-%d %H:%M:%S %z")
   if "comment" in properties:
      try:
         properties["comment"] = str(properties["comment"])
      except:
         raise ValueError("comment could not be parsed into string")
   # A basic validation of the cpt to make sure it can be 'stringed'
   if "cpt" in properties:
      try:
         # if it's a dictionary, parse it as json into a string
         if type(properties["cpt"]) is dict:
            properties["cpt"] = json.dumps(properties["cpt"])
         # if it's a string, send it on
         elif type(properties["cpt"]) is str:
            pass
         # if it's something else, turn it into a string and hope for the best
         else:
            properties["cpt"] = str(properties["cpt"])
      except:
         raise ValueError("CPT cannot be turned into a string")
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
   if "relationship" in properties:
      if properties["relationship"] not in ["described by", "leads to","influences"]:
         raise ValueError("Relationship value %s is not one of the required values('described by', 'leads to', or 'influences'" % properties["relationship"])
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
#      if (properties["confidence"] > 100) or (properties["confidence"] < 0):
#         raise ValueError("Confidence value is out of range 0-100")
   if "comment" in properties:
      try:
         properties["comment"] = str(properties["comment"])
      except:
         raise ValueError("comment could not be parsed into string")
   return properties


# TAKES: a dictionary with "ae"s anchored to originIds and dbId anchored "an"'s in it
# DOES: anchors "ae"s to dbIds
# RETURNS: dictionary of dbId anchored "ae"s
def fixEdges(event):
   aeEvents = event["ae"]
   anEvents = event["an"]
   for edge in aeEvents:
      sourceFound = False
      targetFound = False
#      logging.debug("edge %s has source: %s and target: %s" % (edge, aeEvents[edge]["source"], aeEvents[edge]["target"]))
      if ("source" in aeEvents[edge]) and ("target" in aeEvents[edge]):
         for node in anEvents:
            # if a node existed
#            logging.debug("camparing to node %s with originid: %s" % (node, anEvents[node]["originid"]))
            if aeEvents[edge]["source"] == anEvents[node]["originid"]:
               aeEvents[edge]["originsourceid"] = aeEvents[edge]["source"]
               aeEvents[edge]["source"] = node
               sourceFound = True
            if aeEvents[edge]["target"] == anEvents[node]["originid"]:
               aeEvents[edge]["origintargetid"] = aeEvents[edge]["target"]
               aeEvents[edge]["target"] = node
               targetFound = True
      if (targetFound != True) or (sourceFound != True):
         logging.error("Edge was not anchored to any origin nodes in the Event.  Edge will be removed.")
         del aeEvents[edge]["source"]
         del aeEvents[edge]["target"] 
   return aeEvents

# TODO: Add 'validateCPT' function -> validates against CPT standard add (autogenerated=true when replacing legit one
# TAKES: a CPT dictionary
# DOES: validates it against the CPT format.
# DOES: If the CPT doesn't validate, a default CPT is returned
# RETURNS: The CPT
def validateCPT(graph_db, cpt):
   validated = True
   # make sure there's an nodeid row matching the node
   if "nodeid" not in cpt:
      raise "cpt has no nodeID and cannot be validated"
   n = graph_db.get_node(cpt["nodeid"])
   parents = n.get_related_nodes(direction=-1)
   numRows = 2**len(parents)
   # make sure there's an index row with all the parents in it
   if validated == True:
      if "index" in cpt:
         for parent in parents:
            if parent.id not in "index":
               logging.debug("Validation failed: parent %s not in index" % parent.id)
               validated = False
         if (len("index") - 2) != len(parents):
            logging.debug("Validation failed: parent not in index")
            validated = False
      else:
         logging.debug("Validation failed: index not in cpt")
         validated = False
   if validated == True:
      # Make sure there are 2^parents rows
      for i in range(0,numRows):
         if str(i) not in cpt:
            logging.debug("Validation failed: row %s not in cpt" % i)
            validated = False
         else:
            # make sure the last two nodes are between 0 and 1 inclusive
            if (cpt[str(i)][-1] < 0) or (cpt[str(i)][-1] > 1):
               logging.debug("Validation failed: False not a percentage")
               validated = False
            if (cpt[str(i)][-2] < 0) or (cpt[str(i)][-2] > 1):
               logging.debug("Validation failed: True not a percentage")
               validated = False
            # make sure the rest of the rows represent the binary equiavlent of their row ID
            k = [int(x) for x in list('{0:0b}'.format(j))]
            for l in range(0,len(parents) - len(k)):
               k.insert(0,0)
            if k != cpt[str(j)][:-2]:
               logging.debug("Validation failed: binary %s (%S) did not match row %s, %s" % (j, k, j, cpt[str(j)][:-2]))
               validated = False
   # if anything doesn't validate
   if validated == False:
      # Start from scratch
      cpt = {}
      # Add nodeid property
      cpt["nodeid"] = n.id
      # Add 'reviewed' property & set false
      cpt["reviewed"] = False
      # Add index property
      cpt["index"] = []
      for parent in parents:
         cpt["index"].append(parent.id)
      cpt["index"].append(True)
      cpt["index"].append(False)
      # Get the attribute/anchor parents & event/condition parents
      aParents = []
      ecParents = []
      for c in range(0,len(cpt["index"])-2):
         p = graph_db.get_node(cpt["index"][c])
         if p["class"] in ["attribute", "actor"]:
            aParents.append(c)
         else: #implicitly events/conditions
            ecParents.append(c)
      # Now iterate over the rows to create them
      for i in range(0, numRows):
         ## Create a CPT where nodes w/ all attributes and at least one condition/event are true
         cpt[str(i)] = [int(x) for x in list('{0:0b}'.format(j))]
         for l in range(0,len(parents) - len(k)):
            cpt[str(i)].insert(0,0)         
         # WHAT: If the sum of all of the attribute nodes isn't the length of the nodes (i.e. each is 1 as in all are true)
         # WHAT: And the sum of ecParents is at least 1, (meaning at least one is true)
         # WHAT: then...
         if (sum([cpt[str(i)][x] for x in aParents]) == len(aParents)) and (sum([cpt[str(i)][x] for x in ecParents]) >= 1):
            # Append a 'true' to the string
            cpt[str(i)].append(1) # Append the true
            cpt[str(i)].append(0) # Append the false
         ## all other rows are false
         else:
            cpt[str(i)].append(0) # Append the true
            cpt[str(i)].append(1) # Append the false         
   logging.debug("Returning CPT %s from the validate function" % cpt)
   return cpt # TODO: return the validated or default cpt

# TODO: Add 'fixCPTs' function -> fixes parents 
# TAKES: An updated 'an' dictionary
# DOES: updates the nodeIDs in the CPT form originIDs to dbIDs
# RETURNS: The 'an' dictionary with CPTs anchored to the database
def fixCPTs(graph_db, event):
   logging.debug("Receiving Event %s." % event)
   # Change the CPT parents
   for node in event:
      # Parse the CPT to an object or fail trying
      logging.debug("CPT is  %s of object type %s" % (event[node]["cpt"], type(event[node]["cpt"])))
      try:
         cptObj = json.loads(event[node]["cpt"])
         # change the nodeID
         cptObj["nodeid"] = node
         # Remove the True/False headers, leaving the parent nodes
         parents = cptObj["index"]
         parents.pop()
         parents.pop()
         logging.debug("parents in is %s" % parents) # DEBUG
         # for each of the parents...
         for p in parents:
            # check each node update
            for n in event:
#               logging.debug("P in parents is %s, N in event is %s, OriginID is %s" % (p, n, event[n]["originid"]))
               # to see if the originid matches the parentID in the CPT
               if event[n]["originid"] == p:
                  # if it does, replace the parent id with the new (db anchored) nodeid
                  parents[parents.index(p)] = n
         # put the true/false back on the index and add it back in
         parents.append(True)
         parents.append(False)
         logging.debug("Parents out is %s." % parents)
         cptObj["index"] = parents
         # validate the CPT
         cptObj = validateCPT(graph_db, cptObj)
         # Turn the CPT back into a string and put it back in the event
         event[node]["cpt"] = json.dumps(cptObj)
         # Put it in the database
         g = graph_db.get_node(node)
         g["cpt"] = event[node]["cpt"]
      except Exception as inst:
         logging.error("CPT did not parse into object with error\r\n %s\r\n Returning default CPT" % inst)
         # if it failed, just send back an default CPT by sending validateCPT a blankCPT
         event[node]["cpt"] = json.dumps(validateCPT(graph_db, {"nodeid":node})) 
   logging.debug("Returning Event %s." % event)
   return event # TODO: return updated event, not original


# TODO: Add 'updateCPTs' function -> updates CPT when edges added
# TAKES: An 'ae' or 'dn' dictionary
# DOES: Updates CPTs of associated nodes in the dictionary
# RETURNS: A 'cn' dictionary of changed nodes
# NOTE: This function simply guesses at the CPT.  CPT should be manually validated.
# NOTE: See "CPT Update Approach for reasoning behind why we build the CPTs the way we do.
def updateCPTs(graph_db, event):
   logging.debug("event passed to updateCPTs of type %s is %s" % (type(event), event))
   newEventCN = {}
   # WHAT: Go through the edges & collect the nodes
   # WHY: So we know what to update
   nodes = Set()
   for edge in event:
      logging.debug("Edge is %s, Edge target is %s" % (edge, event[edge]["target"]))
      nodes.add(event[edge]["target"])
#      nodes.add(event[edge]["source"]) # This shouldn't be needed.  Only target should change
   # WHAT: Update the nodes
   # WHY: Because they have new edges
   for node in nodes:
      n = graph_db.get_node(node)
      parents = n.get_related_nodes(direction=-1)
      cptObj = json.loads(n["cpt"])
      numRows = 2**(len(cptObj["index"])-2)
      logging.debug("CPT to be updated is %s" % cptObj)
      newParents = set()
      oldParents = set(cptObj["index"])
      # WHAT: Get the new parents
      # WHY: Because we're going to iterate over it to update the CPT
      for parent in parents:
         if parent.id not in cptObj["index"]:
            newParents.add(parent.id)
      # WHAT: Remove current parents to get old parents
      # WHY: We'll iterate over them to update the CPT
      logging.debug("oldParents is %s before discards" % oldParents)
      oldParents.discard(True)
      oldParents.discard(False)
      for parent in parents:
         logging.debug("Discarding parent %s" % parent.id)
         oldParents.discard(parent.id)
      logging.debug("oldParents is %s" % oldParents)
      # WHAT: Remove old Parents from CPT
      for parent in oldParents:
         logging.info("Removing %s from %s" % (parent, cptObj))
         anyTrue = False
         # get ID of old parent in lists
         i = cptObj["index"].index(parent)
         # Set a counter for the number of rows we've deleted
         deletedCounter = 0
         # WHAT: Iterate throw the rows
         # WHAT: Delete rows where the deleted parent is true
         # WHAT: For the rest of the rows, move them up in the row count
         #        and delete the parent out of them by index
         # WHAT: Keep track of if any non-deleted rows were true &
         #        how many rows we've deleted
         # WHY: Get rid of obselete rows and columns & compress the rows to be contiguious
         for row in range(0,numRows):
            row = str(row) # because they're all strings =P
            logging.debug("Handling row %s, %s, and index %s" % (row, cptObj[row], i))
            if cptObj[row][i] == 1: # if deleted parent is true...
               del cptObj[row] # delete the row
               deletedCounter += 1
            else:
               logging.debug("row %s:%s is False for parent.  False is %s" % (row, cptObj[row], cptObj[row][-1]))
               if cptObj[row][-1] != 1:
                  logging.debug("Setting anyTrue to true")
                  anyTrue = True
               cptObj[row].pop(i)
               if deletedCounter != 0:
                  cptObj[str(int(row)-deletedCounter)] = cptObj[row]
                  del cptObj[row]
         # Delete the deleted parent out of the index
         cptObj["index"].pop(i)
         # Update the row count since it's now half of what it was
         numRows = 2**(len(cptObj["index"])-2)
         logging.debug("new CPT is %s with new numRows %s" % (cptObj, numRows))
         # WHAT: If no rows were true, make the last one true
         # WHY: Because if nothing's true, why have the node?
         if not anyTrue:
            cptObj[str(numRows - 1)][-1] = 0
            cptObj[str(numRows - 1)][-2] = 1
      
      for parent in newParents:
         logging.info("Adding %s to %s" % (parent, cptObj))
         pa = graph_db.get_node(parent)
         # Add newParent to front of index
         cptObj["index"].insert(0, parent)
         # WHAT: Copy all current columns into new columns w/ sequential #'s
         # WHY: So that we can get the right number of rows
         for row in range(0, numRows):
            row = str(row) # because the keys int he CPT are strings
            logging.debug("Number of rows is %s and row  %s is %s" % (numRows, row, cptObj[row]))
            cptObj[str(numRows + int(row))] = cptObj[row][:] # colon to create second object
            # Add "0" at the beginning of the first columns
            cptObj[row].insert(0, 0)
            # Add "1" at the beginning of the second columns 
            cptObj[str(numRows + int(row))].insert(0,1)
            # If new parent is an attribute or actor
            # The logic is easy and can be done int his loop
            if pa["class"] in ["attribute", "actor"]:
               ## make the first half of the rows false
               cptObj[row][len(cptObj["index"])-1] = 1
               cptObj[row][len(cptObj["index"])-2] = 0
            logging.debug("New row %s is %s and row %s is %s" % (row, cptObj[row], (numRows+int(row)), cptObj[str(numRows + int(row))]))
         # If the node is an even or condition
         # The logic is harder and needs to be done separately
         if pa["class"] in ["event", "condition"]:
            # WHAT: Get indexes of attribute/actor parents
            # WHAT: Get indexes of event/condition parents
            # WHY: Because we will use a list of indexes to either add rows to keep or update rows
            aParents = []
            ecParents = []
            for c in range(0,len(cptObj["index"])-2):
               p = graph_db.get_node(cptObj["index"][c])
               if p["class"] in ["attribute", "actor"]:
                  aParents.append(c)
               else: #implicitly events/conditions
                  ecParents.append(c)
            ## iterating over CPT backwards
            trueRows = []
            falseRows = []
            for i in range((numRows * 2) -1, -1,-1):
               i = str(i)
               trueRow = []
               falseRow = []
               logging.debug("numRows is %s, iterator is %s, CPT is %s, and the CPT index is %s" % (numRows, i, cptObj, cptObj["index"]))
               ### if row is non-false (true to any level)
               if cptObj[i][-1] != 1:
                  # Append the row number first
                  trueRow.append(i)
                  # Get the state of attribute parents & the T/F columns
                  for j in range(0,len(aParents)):
                     trueRow.append(cptObj[i][aParents[j]])
                  trueRow.append(cptObj[i][len(cptObj["index"])-2]) # Append the true column
                  trueRow.append(cptObj[i][len(cptObj["index"])-1]) # Append the false column
                  #### Save attr parent state to a list
                  trueRows.append(trueRow)
               # WHAT: Else, make a list of the rows that are false
               # WHY: For rows where the added event/condition is true,
               #       we will take the list of false rows and change them
               #       to match a row where all the attribute parents  are true
               # TODO: This could be improved by also finding the closest
               #        match to the event/condition parents as well
               else:
                  # Append the row number first
                  falseRow.append(i)
                  # Get the state of attribute parents & the T/F columns
                  for j in range(0,len(aParents)):
                     falseRow.append(cptObj[i][aParents[j]])
                  falseRow.append(cptObj[i][len(cptObj["index"])-2]) # Append the true column
                  falseRow.append(cptObj[i][len(cptObj["index"])-1]) # Append the false column
                  #### Save attr parent state to a list
                  falseRows.append(falseRow)
               # WHAT: Iterate over the false rows
            for i in falseRows:
               if i[-1] == 1: # Row is false
                  for r in trueRows:
                     if i[1:-2] == r[1:-2]: # if the attributes of the true row match the false row...
                        ##### copy the true/false from the true state to the false state
                        cptObj[i[0]][len(cptObj["index"])-2] = r[-2] # copy in the 'true'
                        cptObj[i[0]][len(cptObj["index"])-1] = r[-1] # copy in the 'false'
                        break # break the loop (there may be more matches, we don't care.  We're just guessing.
         # update the number of rows to the new value based on the new cpt
         numRows = 2**(len(cptObj["index"])-2)
         logging.info("New CPT is %s" % cptObj)
      # Set the new CPT to unreviewed
      cptObj["reviewed"] = False
      # Save the new CPT to the CPT list
      newEventCN[node] = {"cpt":json.dumps(cptObj)}
      # Save th e new CPT to the Database
      g = graph_db.get_node(node)
      g["cpt"] = json.dumps(cptObj)
   return newEventCN


# TAKES: the graph and event
# DOES: adds the event to the graph
# RETURNS: the event as in the graph (replaced IDs)
# NOTE: Any nodes or edges that fail to validate will not be added and an error logged, but processing will continue
# NOTE: CALL THIS
def addDcesEvent(graph_db, event):
   logging.debug("I just want to appologize at the top to anyone who runs this with debug logging enabled.  There is a TON of crap in here.")
   # Add 'and "DCES_VERSION" in event' to below to check that message
   #   is actually a DCES message, (in case other graph messase are used)
   updatedEvent = {} # empty dictionary for the updated Event
   # "an" must be processed first because AEs may link to ANs
   if "an" in event: # handle add node
      # Add the node to the neo4j database
      updatedEvent["an"] = an_handler(graph_db,event["an"])
      updatedEvent["an"] = fixCPTs(graph_db, updatedEvent["an"])
   if "ae" in event: # handle add edge
      # If nodes were added, make sure edges are referenced to originId
      if "an" in updatedEvent:
         event["ae"] = fixEdges({"ae":event["ae"],"an":updatedEvent["an"]})
      # Add the edge to the neo4j database
      updatedEvent["ae"] = ae_handler(graph_db,event["ae"])
      if "cn" in updatedEvent:
         updatedEvent["cn"] = dict(updatedEvent["cn"].items() + updateCPTs(graph_db, updatedEvents["ae"]).items())
      else:
         updatedEvent["cn"] = updateCPTs(graph_db, updatedEvent["ae"])
   # the order of 'ce/cn's shouldn't matter since they are referenced to dbIds
   if "ce" in event: # handle change edge
      updatedEvent["ce"] = ce_handler(graph_db,event["ce"])
   if "cn" in event: # handle change node
      if "cn" in updatedEvent:
         updatedEvent["cn"] = dict(updatedEvent["cn"].items() + cn_handler(graph_db,event["cn"].items()))
      else:
         updatedEvent["cn"] = cn_handler(graph_db,event["cn"])
   # edges need to be deleted first, otherwise they could get duplcate deletes since the 'dn' can delete edges
   if "de" in event: # handle delete edge
      updatedEvent["de"] = de_handler(graph_db,event["de"])
      if "cn" in updatedEvent:
         updatedEvent["cn"] = dict(updatedEvent["cn"].items() + updateCPTs(graph_db, updatedEvents["de"]).items())
      else:
         updatedEvent["cn"] = updateCPTs(graph_db, updatedEvent["de"])
   if "dn" in event: # handle delete node
      updatedDEDN = dn_handler(graph_db,event["dn"])
      # Add the DN dictionary to the updated event
      updatedEvent["dn"] = updatedDEDN["dn"]
      # If the DE dictionary doesn't exist, create it
      if "de" not in updatedEvent:
         updatedEvent["de"] = {}
      # Copy the deleted edges into the de dictionary
      for edge in updatedDEDN["de"]:
         updatedEvent["de"][edge] = updatedDEDN["de"][edge]
      # Add the dn DCES records to the updated event
      updatedEvent["dn"] = event["dn"]
   # the order of 're/rn's shouldn't matter since they are referenced to dbIds   
   if "re" in event: # handle replace edge
      updatedEvent["re"] = re_handler(graph_db,event["re"])
   if "rn" in event: # handle replace node
      updatedEvent["rn"] = rn_handler(graph_db,event["rn"])
   logging.info("ok, publishing updated event %s" % updatedEvent)
   return updatedEvent

