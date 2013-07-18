'''
 AUTHOR: Gabriel Bassett
 DATE: 07-15-2013
 DEPENDANCIES: networkx, python-dateutil
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

 DESCRIPTION:
 The DCES Module packs and unpacks records in the DCES format.
 The DCES Module will support database records as lists, XML records,
 networkx, and JSON records.

'''

# Imported to handle JSON objects (including DCES objects)
import json
# Imported to allow storage of the construct as a graph
#  this serves as an intermediate stage for the DCES object
import networkx as nx
# Imported to handle XML objects
import xml.dom.minidom
# Imported to generate unique IDs
import uuid
# Imported to allow time parsing
from dateutil import parser
import datetime



## STATIC VARIABLES



## SETUP






## EXECUTION

def json_to_DCES(strIn):
    """(str) -> str

    Takes a JSON record as a string and returns a DCES compliant JSON object
    as a str.

    """
    # Create the basic DCES structure
    strOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # Process Input Here
    return strOut


def list_to_DCES(listIn, columnNames):
    """(list, list) -> str

    Takes a database record as a listobject and returns a DCES compliant
     JSON object as a str.

    Note: Function only checks for times with a column name of "time" or
          "Time" an dother

    """
    # Create the basic DCES structure
    dictOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # Create a time
    if "time" in columnNames:
        time = parser.parse(listIn[columNames.index("time")]).strftime("%Y-%m-%d %H:%M:%S %z")
    elif "Time" in columnNames:
        time = listIn[columNames.index("Time")]
    else:
        time
    # Create a graph to store the construct
    g = nx.DiGraph()
    # Create a unique ID for the constructID node
    CID = uuid.uuid4()
    CID_CPT = json.dumps({"nodeid":CID,"index":[true,false],"0":[1,0]}
    # Create a base constructID node
    g.add_node(
        CID,
        {"cpt": CID_CPT,
         "start":
         }
         )

    # Establish properties for nodes
    # create the node CPT
    nodeCPT = json.dumps({"index":["ID",True,False],"0":[0,1,0],"1":[1,1,0]})
    # if any item is a time
    ##convert it and use as a time
    # else
    ##use current time
    # for each item in the string
    ## make it a node with:
    ### an attribute: "Label":"{'<value from columnName>':<value>
    ### an attribute: time: <the event time or current time if no event time>
    ### an attribute: class: attribute
    ### an attribute: cpt:CPT
    ### an attribute: nodeid:<randomly assigned ID string>
    ### an edge from teh attribute node node to the constructID node

     
    return json.dumps(dictOut)


def xml_to_DCES(strIn):
    """(str) -> str

    Takes an xml string and returns a DCES compliant JSON object as a str.

    """
    # Create the basic DCES structure
    strOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # Process Input Here
    return strOut


def networkx_to_DCES(graphIn):
    """(networkx graph object) -> str

    Takes a networkx graph and returns a DCES compliant JSON object.

    """
    # Create the basic DCES structure
    strOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # Process Input Here
    return strOut


def DCES_to_json(strIn):
    """(str) -> str

    Takes a DCES compliant JSON object as a string and returns a json
     object as a str.

    """
    # load the input as a dictionary
    jsonIn = json.loads(strIn)
    # Create the empty output dictionary
    jsonOut = {}
    # Process Input Here
    return json.dumps(jsonOut)


def DCES_to_list(strIn):
    """(str) -> list, list

    Takes a DCES compliant JSON object as a string and returns a database
     record as a list.

    """
    # load the input as a dictionary
    jsonIn = json.loads(strIn)
    # Create the empty output list
    listOut = []
    # Process Input Here
    return listOut



def DCES_to_xml(strIn):
    """(str) -> str

    Takes a DCES compliant JSON object as a string and returns an xml
     object as a str.

    """
    # load the input as a dictionary
    jsonIn = json.loads(strIn)
    # Process Input Here
    
    # Convert the xml dom object to a string and return
    


def DCES_to_networkx(strIn):
    """(str) -> networkx graph object

    Takes a DCES compliant JSON object as a string and returns a networkx
     graph object.

    """
    # load the input as a dictionary
    jsonIn = json.loads(strIn)
    # Create the empty output graph
    graphOut = nx.DiGraph()
    # process Input Here
    return json.dumps(graphOut)


def main(topic):
   

if __name__ == "__main__":
    main()    
