moirai
======

Summary:
Moirai is an architecture to manage an information security posture in the form of an attack graph. It may be used for offensive tasks such as penetration testing or defensive tasks such as risk assessment and management, intrusion detection, intelligence gathering and application, and response execution.


Implementation:
Moirai is implemented as a pubsub and rpc server in python.  The server provides multiple interfaces to the attack graph stored in a back end neo4j database.  Clients may query the database by way of defined RPCs or may sign up to an appropriate pubsub to receive streaming updates to the graph.  All functionality is expected to be provided by the clients.


Dependancies:
Moirai depends on the py2neo and autobahn python modules.  Additionally, it requires a neo4j database to connect to and store the graph.  There is no facility to run moirai without the neo4j database.

Status:
Moirai is currently unstable and undergoing active development.  The majority of published clients are only test clients for server functionality.


Getting started:
1. Download and install py2neo, autobahn, and neo4j
pip install py2neo
easy-install autobahn
(instructions for installing neo4j can be found at http://www.neo4j.org)
2. clone the repository: 
git clone https://github.com/gdbassett/moirai
3. edit the config file to ensure the values are correct, (primarily server ports and hosts)
nano ~/moirai/server/moirai_server.cfg
4. assuming neo4j hasn't been started, start it
neo4j start (from the neo4j bin directory unless installed as a linux package)
5. start moirai.  Most config options can be overwritten at the command line
python ~/moirai/server/moirai_server.py
(note, the moirai_gui client can be served by enabling the simple python webserver with the "-w" option to moirai_server.py.)
6. Test functionality by running some of the python test clients.  Clients are stored in ~/clients.

