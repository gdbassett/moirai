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
 Script to validate a CPT in a graph

 TODO:


 NOTE:
 To use this validation script, you must have a node with two valid parents
 already in the graph.  Set the nodeid variable to the DBid of that node
 and adjust the parent1 and parent2 variables to the parents prior to
 running.

'''

import moiraiGraphUpdate as moirai

from py2neo import neo4j, cypher

neo4j_host = "localhost"
neo4j_port = "7474"


nodeid = 365
parent1 = 363
parent2 = 362

graph_db = neo4j.GraphDatabaseService("http://" + neo4j_host + ":" + neo4j_port + "/db/data/")


# Try some CPTs
# This one is ok
cpt0 = {u'index': [parent1, parent2, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 1, 1, 0], u'2': [1, 0, 0, 1]}
# This has nothing in it
cpt1 = {"nodeid":nodeid}
# Missing the index
cpt2 = {u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 1, 1, 0], u'2': [1, 0, 0, 1]}
# Index has wrong parents
cpt3 = {u'index': [parent1, 378, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 1, 1, 0], u'2': [1, 0, 0, 1]}
# Index has too many parents
cpt4 = {u'index': [parent1, parent2, 380, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 1, 1, 0], u'2': [1, 0, 0, 1]}
# This is missing a row
cpt5 = {u'index': [parent1, parent2, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'2': [1, 0, 0, 1]}
# "true" is too high
cpt6 = {u'index': [parent1, parent2, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 1, 1.1, 0], u'2': [1, 0, 0, 1]}
# "false" to low
cpt7 = {u'index': [parent1, parent2, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 1, 1, -1], u'2': [1, 0, 0, 1]}
# Row 2 and 3 are not their binary equivalent 
cpt8 = {u'index': [parent1, parent2, True, False],u'nodeid': nodeid, u'reviewed': False, u'1': [0, 1, 0, 1], u'0': [0, 0, 0, 1], u'3': [1, 0, 1, 0], u'2': [1, 1, 0, 1]}

#cpts = [cpt0, cpt1, cpt2, cpt3, cpt4, cpt5, cpt6, cpt7, cpt8]
cpts = [cpt1]

for cpt in cpts:
   print "Validating CPT %s" % cpt
   print moirai.validateCPT(graph_db, cpt)
