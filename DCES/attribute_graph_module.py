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
def bool_to_node(b, key = str(uuid.uuid4()), start_time=datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")):
    """

    :param b: A bool value to be converted to a node
    :param key: Optional key to be associated with the value
    :return: A nx node in DCES attribute schema representing the boolean
    """
    g = nx.DiGraph()
    id = str(uuid.uuid4())
    n = g.add_node(id, {
        'class': 'attribute',
        'attribute': key,
        key: b,
        "start_time": start_time
    }
    return g.node[id]

def main():


if __name__ == "__main__":
    main()
