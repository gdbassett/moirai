__author__ = 'Gabriel Bassett'
'''
 DATE: 07-22-2014
 DEPENDANCIES: a list of modules requiring installation
 Copyright 2014 Gabriel Bassett

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

 DESCRIPTION:
 Provide the functions necessary to turn json to an attribute graph and back.  This includes:
 string -> node
 list -> single depth graph
 Dictionary -> graph
 bool -> node

'''

# USER VARIABLES



########### NOT USER EDITABLE BELOW THIS POINT #################


## IMPORTS
import networkx as nx
import argparse
import json
# Imported to generate unique IDs
import uuid
# Imported to allow time parsing
from dateutil import parser
import datetime


## SETUP
# Parse Arguments (should corrispond to user variables)
parser = argparse.ArgumentParser(description='This script processes a graph.')
#parser.add_argument('db', help='URL of the neo4j graph database', default=NEODB)
# <add arguments here>
args = parser.parse_args()

## EXECUTION
def atomic_to_node(a, key = str(uuid.uuid4()), start_time=datetime.datetime.now()):
    """

    :param b: A atomic variable (bool, string, number, or null) to be converted to a node
    :param key: Optional key to be associated with the value
    :return: A tuple of an nx graph containing the single node and the id string of that node
    """
    g = nx.DiGraph()
    id = key
    g.add_node(id, {
        'class': 'attribute',
        'attribute': key,
        key: a,
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })
    return g, id


def list_to_graph(l, key = str(uuid.uuid4()), col_names = [], start_time=datetime.datetime.now()):
    """

    :param l: a list to turn into a graph
    :param key: Optional key to server as the root of the graph. (Defaults to random UUID)
    :param col_names: a list of the column names associated with the list.  If absent, keys will be column numbers.
    :param start_time: datetime of the time to associate with the node.  (defaults to current time)
    :return: A tuple of an nx graph containing the single node and the id string of that node
    """
    # if there are not column names passed, use column numbers
    for i in range((len(l) - len(col_names))):
        col_names.append(i+1)

    # initialize the graph
    g = nx.DiGraph()

    # Create the root node
    id = key
    g.add_node(id, {
        'class': 'attribute',
        'attribute': key,
        key: a,
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })

    # Add list
    for i in range(len(l)):
        # Create the node
        g.add_node(col_names[i], {
            'class': 'attribute',
            'attribute': col_names[i],
            key: l[i],
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })

        # Connect it to the graph
        g.add_edge(id, col_names[i], {
            "relationship":"described_by",
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        })

    # return the graph and root node
    return g, id


def dict_to_graph(d, key = str(uuid.uuid4()), start_time=datetime.datetime.now()):
    """

    :param d: a dictionary to turn into a graph
    :param key: Optional key to server as the root of the graph. (Defaults to random UUID)
    :param start_time: datetime of the time to associate with the node.  (defaults to current time)
    :return: A tuple of an nx graph representing the dictionary and the id string of that node
    """

    # initialize the graph
    g = nx.DiGraph()

    # Create the root node
    id = key
    g.add_node(id, {
        'class': 'attribute',
        'attribute': key,
        key: a,
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    })

    for key in d.keys():
        if type(d[key]) is dict:
            sub_graph, sub_root_id = dict_to_graph(d[key], key, start_time)
        elif type(d[key]) is list:
            sub_graph, sub_root_id = list_to_graph(d[key], key, start_time=start_time)
        elif type(d[key]) in (str, int, bool, None):
            sub_graph, sub_root_id = atomic_to_node(d[key], key, start_time)
        else:
            return g, id
        g = merge_graphs(g, sub_graph)
        # Even though lower nodes are merged, still need to create the edge from the parent to child
        g.add_edge(id, sub_root_id)

    return g, id

def merge_graphs(g1, g2):
    """

    :param g1: a networkx graph
    :param g2: a networkx graph
    :return: returns the union of the graphs per the CAGS schema
    """
    TODO: Will need to figure out how to get the 2 graphs to merge
    pass


def main():


if __name__ == "__main__":
    main()
