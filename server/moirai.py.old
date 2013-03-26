# Handles the passing of graph information to Moirai
# TODO: Make EVERYTHING lower case

# For Neo4J integration
from py2neo import neo4j, cypher

# For json
import json

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

# format neo4j cypher output into gephi graph streaming format
def cypher_row_handler(graph_db, update):
   pass


# format neo4j cypher metadata output into something returnable
def cypher_metadata_handler(graph_db, update):
   pass

