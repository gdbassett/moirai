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
VERIS_DATA_DIR = "C:///Users/lists_000/Development/VCDB/data/json/"
GRAPH_OUT_FILE = ""


########### NOT USER EDITABLE BELOW THIS POINT #################


## IMPORTS
import networkx as nx
import argparse
import json
# Imported to generate unique IDs
import uuid
# Imported to allow time parsing
import datetime


## SETUP
# Parse Arguments (should corrispond to user variables)
parser = argparse.ArgumentParser(description='This script processes a graph.')
parser.add_argument('--in', help='the directory to read in veris json from', default=VERIS_DATA_DIR)
parser.add_argument('--out', help='output graph file location', default=GRAPH_OUT_FILE)
# <add arguments here>
args = parser.parse_args()


## EXECUTION
 # Was 'None' instead of "" but that doesn't work in graphs
def atomic_to_node(a, key="", start_time=datetime.datetime.now()):
    """

    :param b: A atomic variable (bool, string, number, or null) to be converted to a node
    :param key: Optional key to be associated with the value
    :return: A tuple of an nx graph containing the single node and the id string of that node
    """

    if a is None:
        a = ""  # Was 'None' instead of "" but that doesn't work in graphs

    g = nx.DiGraph()
    r = key
    g.add_node(r, {'class': 'attribute',
                   'attribute': key,
                   key: a,
                   "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                  })
    return g, r


 # Was 'None' instead of "" but that doesn't work in graphs
def list_to_graph(l, key="", col_names=list(), start_time=datetime.datetime.now()):
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
    r = key
    g.add_node(r, {'class': 'attribute',
                   'attribute': key,
                   key: "",  # Was 'None' instead of "" but that doesn't work in graphs
                   "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                  })

    # Add list
    for i in range(len(l)):
        # Create the node
        g.add_node("col_{0}".format(col_names[i]), {'class': 'attribute',
                                                    'attribute': "col_{0}".format(col_names[i]),
                                                    "col_{0}".format(col_names[i]): l[i],
                                                    "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                                                   })

        # Connect it to the graph
        g.add_edge(r, "col_{0}".format(col_names[i]), {"relationship": "described_by",
                                                       "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                                                      })

    # return the graph and root node
    return g, r


 # Was 'None' instead of "" but that doesn't work in graphs
def dict_to_graph(d, key="", start_time=datetime.datetime.now()): # bottom up implementation
    """

    :param d: a dictionary to turn into a graph
    :param key: Optional key to server as the root of the graph. (Defaults to random UUID)
    :param start_time: datetime of the time to associate with the node.  (defaults to current time)
    :return: A tuple of an nx graph representing the dictionary and the id string of that node
    """

    # initialize the graph
    g = nx.DiGraph()

    # Create the root node id
    if key == "":  # Was 'None' instead of "" but that doesn't work in graphs
        r = str(uuid.uuid4())
    else:
        r = key


    for key in d.keys():
        if type(d[key]) is dict:
            sub_graph, sub_root_id = dict_to_graph(d[key], key, start_time)
        elif type(d[key]) is list:
            sub_graph, sub_root_id = list_to_graph(d[key], key, start_time=start_time)
        elif type(d[key]) in (str, int, bool, None):
            sub_graph, sub_root_id = atomic_to_node(d[key], key, start_time)
        else:
            return g, r

        # add the root node to the subgraph.  (facilitates merging)
        sub_graph.add_node(r, {'class': 'attribute',
                               'attribute': key,
                               key: "",  # Was 'None' instead of "" but that doesn't work in graphs
                               "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                              })
        sub_graph.add_edge(r, sub_root_id, {"relationship": "described_by",
                                            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                                           })

        # Merge the sub_graph into the main graph
        g = merge_graphs(g, sub_graph)

        g = nx.relabel_nodes(g, {'g-' + r: r, 'h-' + r: r})
#        g = nx.relabel_nodes(g, {'h-' + r: r})

#        print "{0} - {1}".format(r, g.edges()) # DEBUG

    return g, r


def dict_to_graph_2(d, key="", start_time=datetime.datetime.now()): # alternate implementation, top-down
    """

    :param d: a dictionary to turn into a graph
    :param key: Optional key to server as the root of the graph. (Defaults to random UUID)
    :param start_time: datetime of the time to associate with the node.  (defaults to current time)
    :return: A tuple of an nx graph representing the dictionary and the id string of that node
    """
    g = nx.DiGraph()
    r = ""  # Was 'None' instead of "" but that doesn't work in graphs

    # create the list of nodes to parse into the graph in the form (parent, key, node)
    queue = [(None, key, d)] # Was 'None' instead of "" but that doesn't work in graphs

    g.add_node(key, {'class': 'attribute',
                     'attribute': key,
                     key: ""
                    })

    while len(queue) > 0:
        node = list(queue.pop(0))
        # Create the node id
        try:
            n = str(node[1]) + str(uuid.uuid4())

            if type(node[2]) == dict:
                # Enqueue children
                for k in node[2].keys():
                    queue.append((n, k, node[2][k]))

                # Create the node
                g.add_node(n, {'class': 'attribute',
                               'attribute': node[1],
                               node[1]: "",  # Was 'None' instead of "" but that doesn't work in graphs
                               "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                              })

                # link to parent
                if node[0] is not None:  # Was 'None' instead of "" but that doesn't work in graphs
                    g.add_edge(node[0], n, {
                        "relationship": "described_by",
                        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })
                else:
                    r = n

            elif type(node[2]) in (str, int, bool, None):
                if node[2] is None:
                    node[2] = ""  # Was 'None' instead of "" but that doesn't work in graphs

                # find nodes that match the attributes and have no children
                m = [x[0] for x in g.nodes(data=True) if (node[1] in x[1] and x[1][node[1]] == node[2] and len(g.successors(x[0])) == 0)]

                if len(m) > 0: # a duplicate exists so link to it instead
                    n = m[0]
                else: # no duplicate exists.  create the node
                    g.add_node(n, {
                        'class': 'attribute',
                        'attribute': node[1],
                        node[1]: node[2],
                        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })

                # link to parent
                if node[0] is not None:
                    g.add_edge(node[0], n, {
                "relationship":"described_by",
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            })
                else:
                    r = n

            elif type(node[2]) == list:
                # Create the list root
                g.add_node(n, {
                    'class': 'attribute',
                    'attribute': node[1],
                    node[1]: "", # Was 'None' instead of "" but that doesn't work in graphs
                    "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                })

                # link to parent
                if node[0] is not None: # Was 'None' instead of "" but that doesn't work in graphs
                    g.add_edge(node[0], n, {
                        "relationship":"described_by",
                        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })
                else:
                    r = n

                # enqueue individual list items
                for k in range(len(node[2])):
                    queue.append((n, str(key) + "_col" + str(k+1), node[2][k]))

        except Exception as e:
            print queue
            print node
            raise e

    return g, r


def dict_to_graph_3(d, key = "", start_time=datetime.datetime.now()): # alternate implementation, top-down
    """ Another alternate way of processing dictionary with no intermediary nodes

    :param d: a dictionary to turn into a graph
    :param key: Optional key to server as the root of the graph. (Defaults to random UUID)
    :param start_time: datetime of the time to associate with the node.  (defaults to current time)
    :return: A tuple of an nx graph representing the dictionary and the id string of that node
    """
    g = nx.DiGraph()

    # create the nested keys, values to parse
    queue = [(key, d)] # Queue of dictionaries to explore

    try:
        # create dictionary record root node
        n = str(key) + str(uuid.uuid4())
        g.add_node(n, {
            "class": "attribute",
            "attribute": "record",
            "record": n
        })

        # process dictionary as a queue
        while len(queue) > 0:
            node = queue.pop(0)

            if type(node[1]) == dict:
                queue = queue + [(node[0], x) for x in node[1].values()]

            elif type(node[1]) == list:
                # enqueue individual list items
                for k in range(len(node[1])):
                    queue.append((str(key) + "_col" + str(k+1), node[1][k]))

            elif type(node[1]) in (str, int, bool, None):
                if node[1] == None:
                    node[1] = ""  # Was 'None' instead of "" but that doesn't work in graphs

                # find nodes that match the attributes and have no children
                m = []
                for x in g.nodes(data=True):
                    if node[0] in x[1] and x[1][node[0]] == node[1] and len(g.successors(x[0])) == 0:
                        m.append(x[0])

                if len(m) > 0: # a duplicate exists so link to it instead
                    nid = m[0]
                else: # no duplicate exists.  create the node
                    nid = uuid.uuid4()
                    g.add_node(nid, {
                        'class': 'attribute',
                        'attribute': node[0],
                        node[0]: node[1],
                        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })

                # link to parent
                    g.add_edge(n, nid, {
                        "relationship":"described_by",
                        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                    })

    except Exception as e:
        print queue
        print node
        raise e

    return g, n

def merge_graphs(g, h, attributes = list(), merge_parents = False):
    """

    :param g: a networkx graph
    :param h: a networkx graph (preferably the smaller graph being added to g)
    :param attributes: A list of attributes to match on.  If present, all other attributes will be Don't Care's
    :param merge_parents: If True, nodes that have children will still be merged.  Default is 'False'
    :return: returns the union of the graphs per the CAGS schema
    """
    # TODO: ADD the ability to pass in a set of edges which will also be created manually. (link graph roots, etc)
    #       Alternately, users could be expected to create edges by retrieving nodes by attribute

    # create  a union graph
    G = nx.union(g, h, rename=('g-', 'h-'))

    # Look through graph for duplicates
    for n1 in h.nodes(data=True):
        # The None:None node is likely to be a root node in a nested dictionary so don't merge it
        if not ("" in n1[1] and n1[1][""] == "") and \
                (merge_parents == True or len(g.successors(n1[0])) == 0):  # Was 'None' instead of "" but that doesn't work in graphs
            for n2 in g.nodes(data=True):
                # Match nodes
                match = True
                if len(attributes) == 0:
                    if n1[1] != n2[1]:
                        match = False
                else:
                    # for each attribute to match...
                    for attribute in attributes:
                        # check if node 1 has the attribute
                        if attribute in n1[1]:
                            # if it does, match is false if n2 doesn't have the attribute or has a different value
                            if attribute not in n2[1] or n1[1][attribute] != n2[1][attribute]:
                                match = False
                if match:
                    # if there is a duplicate based on attributes, merge the nodes
                    G = nx.relabel_nodes(G, {"h-" + n1[0]:"g-" + n2[0]})
                    print "matched, {0} and {1}".format(n1[0], n2[0])

    return G

def main():
    # initialize blank graph
    G = nx.DiGraph()

#    TODO:
    # read the VCDB JSON directory
    # for each record:
        # Create a graph tree from the record w/ the filename as the root
        # create a record:<filename> node and point it to each node in the tree
        # merge it with the rest of the graph
        # add it to a root hierarchy (either from the record's root or record node)

    # save graph
    nx.write_graphml(G, args.out)

if __name__ == "__main__":
    main()
