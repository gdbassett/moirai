'''
 AUTHOR: Gabriel Bassett
 DATE: 07-15-2013
 DEPENDANCIES: networkx
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


import json
import
import networkx as nx
import xml.dom.minidom

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

    """
    # Create the basic DCES structure
    strOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # Create a base constructID node
    # CPT = {"index":["J",true,false],"0":[0,1,0],"1":[1,1,0]}}
    # if any item is a time
    ##convert it and use as a time
    # else
    ##use current time
    # for each item in the string
    ## make it a node with:
    ### Time
    ### TODO: keep completing

     
    return strOut


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
