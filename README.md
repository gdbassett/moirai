#moirai
======

##Summary:
Moirai is a patent pending, open source licensed, architecture to manage an information security posture in the form of an attack graph. It may be used for offensive tasks such as penetration testing or defensive tasks such as risk assessment and management, intrusion detection, intelligence gathering and application, and response execution.

Moirai is the metasploit of defense.  It is a central framework with which all other defensive tools can communicate.

Moirai has three explicit tasks:
* Receive infosec events
* Validate that the events meet standard event and graph formats
* Provide the events to clients which wish to receive them

##Implementation:
Moirai is implemented as a pubsub and rpc server in python.  The server provides multiple interfaces to the attack graph stored in a back end neo4j database.  Clients may query the database by way of defined RPCs or may sign up to an appropriate pubsub to receive streaming updates to the graph.  All functionality is expected to be provided by the clients.


##Dependancies:
Moirai depends on thepy2neo, autobahn, and python-dateutil python modules.  Additionally, it requires a neo4j database to connect to and store the graph.  There is no facility to run moirai without the neo4j database.

##Status:
* Previously - Moirai has reached Milestone 0.  It is capable of receiving graph events in WAMP format, saving them to the graph, and redistributing them across the pubsub. It also is able to execute cyphers by RPC.

* 3/26/13 - Moirai has reached Milestone 1.  It is capable of receiving graph events, validating them against the rules outlined in protocol_definitions.txt, fixing them up if possible, and redistributing them.  An additional RPC to retrieve the entire graph has been added.

* Future - Milestone 2: Cypher and Construct RPCs - Milestone 2 will support additional cyphers, specifically RPCs to implement additional cyphers and automated processing of DCES constructs.  It will facilitate intelligence gathering and intrusion detection utilizing the graph

* Future - Milestone 3: GUI and Client Service pubsub - Milestone 3 is designed to support clients which require manual addition of information to the grpah and which provide their own RPCs.

* Future - Milestone 4: Multiple Clients Available - Implementation of multiple potential clients.

* Future - Milestone 5: Robust Server - Improvements in the Moirai server to facilitate enterprise use.

(Please note, milestones may not be implemented in chronological order and are subject to change without notice.)

##Getting started:
1. Download and install py2neo, autobahn, and neo4j
```
pip install py2neo autobahn python-dateutil
```
(instructions for installing neo4j can be found at http://www.neo4j.org)
2. clone the repository: 
```
git clone https://github.com/gdbassett/moirai
```
3. edit the config file to ensure the values are correct, (primarily server ports and hosts)
```
nano ~/moirai/server/moirai_server.cfg
```
4. assuming neo4j hasn't been started, start it
```
neo4j start
```
(from the neo4j bin directory unless installed as a linux package)
5. start moirai.  Most config options can be overwritten at the command line
```
python ~/moirai/server/moiraiServer.py
```
(note, once fully implemented, the moirai_gui client can be served by enabling the simple python webserver with the "-w" option to moirai_server.py.)
6. Test functionality by running some of the python test clients.  Clients are stored in ~/clients.
