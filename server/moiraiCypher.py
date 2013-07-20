'''
 AUTHOR: Gabriel Bassett
 DATE: 07-15-2013
 DEPENDANCIES: py2neo
 Copyright 2013 Gabriel Bassett

 LICENSE:
 This program is free software:  you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 or the LIcense, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public LIcense for more dtails.

 You should have received a copy of the GNU General Public License
 along with theis program.  If not, see <http://www.gnu.org/licenses/>.

 ACKNOWLEDGEMENTS:
 

 DESCRIPTION:
 Interface to neo4j attack graph to execute cypher queries
 Provide those functions to the moirai server to execute

 TODO:


 NOTES:

 
'''



### INCLUDES ###


# For Neo4J integration
from py2neo import neo4j, cypher

# For json
import json


### STATIC VARIABLES ###



### Set Environment ###



### CLASS AND METHOD DEFINITIONS #### 


# format neo4j cypher output into gephi graph streaming format
def cypher_row_handler(graph_db, update):
   pass




# format neo4j cypher metadata output into something returnable
def cypher_metadata_handler(graph_db, update):
   pass


def getState():
      query1 = "START n=node(*) RETURN n;"
      query2 = "START n=node(*) MATCH n-[r]->m RETURN r, ID(n), ID(m);"
      params = {}
      print "exporting state"
      # get all nodes
      # pass each row to cypher2pubsub to change into DCES events
      cypher.execute(graph_db, query1, params, 
                     row_handler=self.cypher2pub)
      # get all edges (retrieve by nodes?)
      cypher.execute(graph_db, query2, params,
                     row_handler=self.cypher2pub)
      return True



# TODO: Make "params" optional
# TODO: check topic list before executing
def cypher(self, query, params):
  print "RPC Directory:" # DEBUG
  print dir(self)
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


# Takes a query
# Returns the nodes/edges from the query across the pubsub
# NOTE: As this uses the cypher2pub method, it will only return ..
#        nodes and edges, and only if they are the first field int he query.
def pubCypher(self, query, params):
  cypher.execute(graph_db, query, params, 
                 row_handler=self.cypher2pub)
