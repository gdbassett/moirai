'''
 AUTHOR: Gabriel Bassett
 DATE: 07-15-2013
 DEPENDANCIES: networkx, python-dateutil
 Copyright 2013 Gabriel Bassett
 Version: DCES 0.3

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
def parse_dict(dictIn):
    """(dict) -> dict, str

    Takes a JSON record and returns a DCES graph and the root node of that graph
     as a string.

    """

    # DCESDict = {"an":{}, "ae":{}}
    for key in dictIn:
        ## if dict
        if type(dictIn[key]) = dict:
            ### create branching node
            rootId = str(uuid.uuid4())
            rootNode = {rootID:{"cpt": json.dumps({"nodeid":CID}),
                                "class":"attribute",
                                "start": "",
                                "label":json.dumps({"key":key})}}
            # START HERE
    ### parse dict
    ### add edge from returned node to created branch node
    ## else
    ### build node dict
    # If any nodes in dict don't had a time, search for a time and add it
    #   Starting with root node
    # return DCESDict


def json_to_DCES(strIn):
    """(str) -> str

    Takes a JSON record as a string and returns a DCES compliant JSON object
    as a str.

    """
    # Create the basic DCES structure
    dictOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # Create construct ID
    # Create template node string
    # Convert json string to dict
    nodes = parse_dict(json.loads(strIn)
    # for each node that has no time, add the time
    
    return json.dumps(dictOut)


def list_to_DCES(listIn, columnNames):
    """(list, list) -> str

    Takes a database record as a listobject and returns a DCES compliant
     JSON object as a str.

    Note1: Function checks for times with a column name of "startTime", "time", 
        or "Time" in the columnNames.  If it isn't found, current time is used.

    Note2: Functions will check for endTime.  If it finds it, nodes will be
           populated.

    """
    # Check that the 2 lists are the same thing
    if len(listIn) != len(columnNames):
        raise ValueError("The lengths of the two supplied lists must match")
    
    # Create the basic DCES structure
    dictOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    try:
        # Create a start time
        if "startTime" in columnNames:
            startTime = parser.parse(listIn[columNames.index("startTime")]).strftime("%Y-%m-%d %H:%M:%S %z")
        elif "time" in columnNames:
            startTime = parser.parse(listIn[columNames.index("time")]).strftime("%Y-%m-%d %H:%M:%S %z")
        elif "Time" in columnNames:
            startTime = parser.parse(listIn[columNames.index("Time")]).strftime("%Y-%m-%d %H:%M:%S %z")
        elif "Start" in columnNames:
            startTime = parser.parse(listIn[columNames.index("Start")]).strftime("%Y-%m-%d %H:%M:%S %z")
        elif "start" in columnNames:
            startTime = parser.parse(listIn[columNames.index("start")]).strftime("%Y-%m-%d %H:%M:%S %z")
        else:
            startTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
    except ValueError:
            startTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")        
    # Create an end time if possible
    try:
        if "endTime" in columnNames:
            endTime = parser.parse(listIn[columNames.index("endTime")]).strftime("%Y-%m-%d %H:%M:%S %z")
        if "end" in columnNames:
            endTime = parser.parse(listIn[columNames.index("end")]).strftime("%Y-%m-%d %H:%M:%S %z")
        if "End" in columnNames:
            endTime = parser.parse(listIn[columNames.index("End")]).strftime("%Y-%m-%d %H:%M:%S %z")
        else:
            endTime = None
    except ValueError:
        endTime = None
    # Create a graph to store the construct
    g = nx.DiGraph()
    # Create a unique ID for the constructID node
    CID = str(uuid.uuid4())
    CID_CPT = {"nodeid":CID}
    # Create a base constructID node
    dictOut["an"][CID] = 
        {"cpt": json.dumps(CID_CPT),
         "class":"attribute",
         "start": startTime,
         "label":json.dumps({"id":CID})
         }
    if endTime:
        dictOut["an"][CID]["end"]: endTime
        
    # Establish properties for nodes
    # create the node CPT
    nodeCPT = {"nodeid":"ID","index":[true,false],"0":[1,0]}
    # for each item in the string
    for i in range(len(columnNames)):
        ## if it's not one of the labels we used
        if columnNames[i] not in ["time", "Time", "startTime", "endTime", "End", "end", "Start", "start"]:
            nodeID = str(uuid.uuid4())
            ## make it a node with:
            nodeCPT["nodeid"] = nodeID
            dictOut["an"][nodeID] = 
                {"cpt": loads(nodeCPT).replace("ID",nodeID),
                 "class":"attribute",
                 "start": startTime,
                 "label":loads({columnNames[i]:listIn[i]})
                 }
            ### an edge from the attribute node node to the constructID node
            edgeID = str(uuid.uuid4())
            dictOut["ae"][edgeID] = {
                "source":nodeID,
                "target":CID,
                "directed":True,
                "relationship":"described by",
                "start":startTime
                }
            # If an end time exists, store it on the node and edge
            if endTime:
                dictOut["an"][nodeID]["end"] = endTime
                dictOut["ae"][edgeID]["end"] = endTime

    # Return the DCES dictionary as a string
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
    dictOut = {"dces_version":"0.3", "ae":{}, "an":{}}
    # create default CPT
    nodeCPT = {"nodeid":"ID","index":[true,false],"0":[1,0]}
    blankCPT = {"nodeid":"ID"}
    # TODO:  Create construct ID node here
    CID = str(uuid.uuid4())
    dictOut["an"][CID] = {
        "cpt": json.dumps(blankCPT).replace("ID",CID),
         "class":"attribute",
         "start": startTime,
         "label":json.dumps({"id":CID})
         }= {
                    
                    }
    # Iterate over all nodes
    for nKey in graphIn.node:
        # Going to have to parse out attributes from the node into new nodes
        # Pull Start, End, Comment and Label values and store them
        # See if graph has a real start time in it
        if 'start' in graphIn.node[nKey]:
            try:
                startNode = False
                startTime = parser.parse(graphIn.node[nKey]["start"]).strftime("%Y-%m-%d %H:%M:%S %z")
            except ValueError:
                startNode = True
                startTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

        else:
            startNode = True
            startTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
        # See if graph has a real end time in it
        if 'end' in graphIn.node[nKey]:
            try:
                endNode = False
                endTime = parser.parse(graphIn.node[nKey]["end"]).strftime("%Y-%m-%d %H:%M:%S %z")
            except ValueError:
                endNode = True
                endTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")

        else:
            endNode = True
            endTime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")
        # get comments if any
        if 'comment' in graphIn.node[nKey]:
            comment = graphIn.node[nKey]['comment']
        else
            comment = None
        # try and import the label, parsing it if necessary
        if 'label' in graphIn.node[nKey]:
            # check if it's a dictionary
            if type('label') == dict:
                labelNode = False
            else:
                labelNode = True
                
            # if it is, keep 1 value from it
        # Create core node
        if not labelNode:
            dictOut["an"][nKey] = {'label':graphIn.node[nKey]['label']}
        else
            dictOut["an"][nKey] = {'label':json.dumps({'id':nKey})}
        dictOut["an"][nKey]['start'] = start
        dictOut["an"][nKey]['end'] = end
        if comment:
            dictOut["an"][nKey]['comment'] = comment
            
        # For all node attributes
        for a in graphIn.node[nKey]:
            # If it's a node we're not going to create, pass
            if a = 'start' and not startNode:
                pass
            elif a = 'comment':
                pass
            elif a = 'end' and not endNode:
                pass
            elif a = 'label' and not labelNode:
                pass
            else
                # if it's a node we are going to create
                ## Create an attribute node for that attribute
                key = str(uuid.uuid4())
                dictOut["an"][key] = {'label': loads({a: graphInnode[nKey][a]}),
                                     "class":"attribute",
                                     "cpt": json.dumps(nodeCPT).replace("ID",nKey)
                                    }
                ## Populate start, commment, and end
                dictOut["an"][key]['start'] = start
                if end:
                    dictOut["an"][key]["end"] = end
                if comment:
                    dictOut["an"][key]["comment"] = comment
                ## Create an edge linking the attribute to the core node
                dictOut["an"][str(uuid.uuid4())] = {
                    "source":nKey,
                    "target":key,
                    "directed":True,
                    "relationship":"described by",
                    "start":start
                    }
                ## Create an edge linking the attribute to the constructID
                dictOut["ae"][str(uuid.uuid4())] = {
                    "source":key,
                    "target":CID,
                    "directed":True,
                    "relationship":"described by",
                    "start":start
                    }                    

    # Parse all the edges
    for e in graphIn.edges():
        # Get the source from the edge
        source = e[0]
        # get the target from the edge
        target = e[1]
        # Get the attribute dict from the edge
        attr = g[source][target]
        # id
        EID = str(uuid.uuid4())
        
        dictOut["ae"][EID] = {
            "source":source,
            "target":target,
            "directed":True,
            "relationship":"described by",
            "start":start
            }
                
    return json.dumps(dictOut)


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
    columnNames = []
    # Find the constructID node
    for node in jsonIn["an"]:
        if "id" in loads(jsonIn[node]["label"]):
            CID = node
            break

    # Add cross-node attributes first from constructID node
    # Add the start time
    listOut.append(jsonIn["an"][CID]["start"])
    columnNames.append("start")
    # If there's an end time, include it
    if "end" in jsonIn["an"][CID]
        listOut.append(jsonIn["an"][CID]["end"])
        columnNames.append("end")
    # If there's a comment, include it
    if "comment" in jsonIn["an"][CID]
        listOut.append(jsonIn["an"][CID]["comment"])
        columnNames.append("comment")
    # Parse all the nodes, and if they are an attribute, import their label
    for node in jsonIn["an"]:
        label = json.loads(jsonIn["an"][node]["label"])
        # Import one key per node
        for key in label:
            listOut.append(label[key])
            columnNames.append(key)
            break
        

    return listOut, columnNames


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
