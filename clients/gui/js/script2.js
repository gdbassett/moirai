/////////////////////////////////
// Moirai GUI
// CC Gabriel Bassett
// Reads web sockets from a gephi graph stream, displays them, and allows editing/saving of the CPT
// TODO: Update to better simplify CPT creation:
//       1. when editing a 'true' value, the 'false' should be 1-true
//       2. When editing a 'true' value above 0, all true values above 0 below it in the CPT should take the value
// TODO: Make a universal graph editor
//       1. Make all node fields editable
//       2. Provide for adding/deleting nodes
//       3. Create an edge table to add, delete, and edit edges
//       4. Display the entire graph in a Sigmajs canvas
// TODO: Make it pretty
//       1. Divide up the page into regions (head, left(table), right(canvas), foot)
//       2. Add some color, styling to the regions of the page
// TODO: Convert to coffeescript

//Variables
var socket = null;
//bool was temporary and probably no longer needed
//var bool = true;
var addressBox = null;
var logBox = null;
//edges needs to be replaced with a more appropriate object for the graph
//var edges = [];
//create the empty graph object
var g = {};
// WAMP session object
var sess = null;
// App names to prefix
var app_domain = "informationsecurityanalytics.com"
var app_name = "moirai"


//jQuery initialization function
$(document).ready(function() {
    
    // Variables used by connection function which is non-jQuery based
    addressBox = document.getElementById('address');
    logBox = document.getElementById('log');

    
    //TODO: Create Graph object
    create_empty_graph();

    
    // Catch input to message box (sends commands back on WS)
    $('#text').keypress(function(event) {  
        if (event.keyCode == '13') {  
            send($('#text').val());  
        }
    });

   
    //Bug: Doesn't work.
    //When you click the cpt cell of the table, reveal the CPT form
    $(document).on('click', '.cpt', function() {
        $('.cpt_form').hide();
        $(this).find('form').show();
        canvasIt($(this).attr('id').substr(3));
    });
    

//BUG: This doesn't work
    //Initialize graph canvas
    var sigRoot = document.getElementById("myCanvas");
    sigInst = sigma.init(sigRoot);

    
    
    //Sort the nodesTable
    var inverse = false;
    $(document).on('click', 'th', function(){
        
        var header = $(this),
            index = header.index();
            
        header
            .closest('table')
            .find('td')
            .filter(function(){
                return $(this).index() === index;
            })
            .sortElements(function(a, b){
                
                a = $(a).text();
                b = $(b).text();
                
                return (
                    isNaN(a) || isNaN(b) ?
                        a > b : +a > +b
                    ) ?
                        inverse ? -1 : 1 :
                        inverse ? 1 : -1;
                    
            }, function(){
                return this.parentNode;
            });
        
        inverse = !inverse;
        
    });
    
});

// TODO: Replacing with autobahn-based WAMP websocket connection
// Opens web socket
// accepts events on websocket
// closes websocket
// calls addtolog for everything
function connect() {
  if ('WebSocket' in window) {
    socket = new WebSocket(addressBox.value);
  } else if ('MozWebSocket' in window) {
    socket = new MozWebSocket(addressBox.value);
  } else {
    return;
  }

  socket.onopen = function () {
    addToLog('Opened');
  };
  socket.onmessage = function (event) {
    updateGraph(event.data);
    //Should pull the update type out of the message
    switch (event.data.substr(2,2)) {
        case "an":
            var nodeId = event.data.split("\"",4)[3];
            update_node_table(nodeId);            
            break;
        case "cn":
            var nodeId = event.data.split("\"",4)[3];
            update_node_table(nodeId);
            break;
    };
        
//    if(event.data.substr(2,2) === "an") {
//        //Should pull the NodeID out of the string by splitting at quotes and taking the 3rd item in the resulting array
//        var nodeId = event.data.split("\"",4)[3];
//        update_node_table(nodeId);
//    };
    addToLog('< ' + event.data);
  };
  socket.onerror = function () {
    addToLog('Error');
  };
  socket.onclose = function (event) {
    var logMessage = 'Closed (';
    if ((arguments.length == 1) && ('CloseEvent' in window) &&
        (event instanceof CloseEvent)) {
      logMessage += 'wasClean = ' + event.wasClean;
      // code and reason are present only for
      // draft-ietf-hybi-thewebsocketprotocol-06 and later
      if ('code' in event) {
        logMessage += ', code = ' + event.code;
      }
      if ('reason' in event) {
        logMessage += ', reason = ' + event.reason;
      }
    } else {
      logMessage += 'CloseEvent is not available';
    }
    addToLog(logMessage + ')');
  };

  addToLog('Connect ' + addressBox.value);
}
// END CONNECT

function connect2() {
  ab.connect(addressBox.value,

    // WAMP session was established
    function (session) {

      sess = session;

      console.log("Connected to " + addressBox.value);
      // Now that the WAMP session is connected, do something:
      //Prefix the connection
      sess.prefix("moirai", "http://" + app_domain + "/" + app_name + "/");

      //Subscribe to the pubsub as graph state will come over it
      sess.subscribe("moirai:graph1",
        // on event publication callback
        function (topic, event) {
          // Log it so we know what happened
          addtolog("got event: " + event);
          // Add it into the graph object
          updateGraph(event);
          // Convert it to a JSON object
          var eventObject = JSON.parse(event);
          // Get the event type
          for (key in eventObject) {
            // If this is a change to nodes,
            if (key in {"an":"", "cn":"", "rn":""}) { // This treats CNs as RNs & doesn't handle DNs
              // Get the node id
              for (nodeId in eventObject[key]) {    
                // Update the node table
                // TODO: better handle nodes
                update_node_table(nodeId);
              }
            }
          }
      });
    },


    // WAMP session is gone
    function (code, reason) {

      sess = null;

      if (code == ab.CONNECTION_UNSUPPORTED) {
        window.location = "http://autobahn.ws/unsupportedbrowser";
      } else {
        alert(reason);
      }
    }
  );
}


// Logs ws information to a text box
function addToLog(log) {
    logBox.value += log + '\n';
    logBox.scrollTop = 100000;
};
    

//TODO
//This function should take a event data (which on load is
//the entire graph) and parse it.  It should:
//0. If the node/edge exists, delete it from the graph object & node table
//1. Create a javascript object holding the entire graph (in json?)
//3. If a CPT exists, pass it to the CPT-stringify function to stringify
//4. If a CPT does'n't exist, call the CPT-stringify function with nothing (& get generic CPT)
//2. Create the table row for the node, storing the nodeID, Label, class, & CPT Table into it.
//6. Resort the table based on NodeID
function updateGraph(event_data) {
    eventObj = {};
    eventArray = [];
    //parse the event data into a json object
    eventObj = jQuery.parseJSON(event_data);
    //break the event type and event id off the rest of the object
    eventArray = parse_json_event(eventObj);
    //Update the graph object
    switch (eventArray[0]) {
        case "an":
            //Update Node
            graphAddNode(eventArray);
            break;
        case "ae":
            //Update Edge
            graphAddEdge(eventArray);
            break;
        case "cn":
            graphAddNode(eventArray);
            break;
    };

// Changed to switch above
//    if (eventArray[0] == "an") {
//        //Update Node
//        graphAddNode(eventArray);
//    } else if (eventArray[0] == "ae") {
//        //Update Edge
//        graphAddEdge(eventArray);
//    };
};

    
// takes a parsed graph event object.
// returns an array of values
// array[0] = type (ae or an), array[1] = Id, array[2] = everything else.
function parse_json_event(event_obj) {
    array = [];
    for (var key in event_obj) {
        array[0] = key;
        for (var key2 in event_obj[key]) {
            array[1] = key2;
            array[2] = event_obj[key][key2];
        };
    };
    return array;
};


//edge constructor
function edge(id, source, target, attr_array) {
    this.id =  id;
    this.source = source;
    this.target = target;
    this.attr_array = attr_array;
}

//node constructor
function node(id, attr_array) {
    this.id = id;
    this.attr_array = attr_array;
}

//creates an empty graph
function create_empty_graph() {
    g.edges = new Array();
    g.nodes = new Array();
}


//Takes an edge Array
//updates it in the graph (g)
function graphAddEdge(edgeArray) {
    if (g.edges.hasOwnProperty(g.edges[edgeArray[1]])) {
        //First get the existing edge
        var tempEdge = new edge(g.edges[edgeArray[1]], g.edges[edgeArray[1]]['source'], g.edges[edgeArray[1]]['target'], g.edges[edgeArray[1]]['attr_array']);
        // Then copy in the update, item by item
        tempEdge['source'] = edgeArray[2]['source'];
        tempEdge['target'] = edgeArray[2]['target'];
        for (var key in edgeArray[2]) {
            tempEdge['attr_array'][key] = edgeArray[2][key];
        };
        //Delete the source/destination out of the attributes
        delete tempEdge['attr_array']['target'];
        delete tempEdge['attr_array']['source'];
    } else {
        var tempEdge = new edge(edgeArray[1], edgeArray[2]['source'], edgeArray[2]['target'], edgeArray[2]);
        delete tempEdge['attr_array']['target'];
        delete tempEdge['attr_array']['source'];
    }
    // Finally store it back into the graph
    g.edges[tempEdge.id] = tempEdge;
    
    // If the node is already in the table.  and doesn't have a valid PT
    if (g.nodes.hasOwnProperty(tempEdge.target)) {
        //console.log("Adding edge with target " + tempEdge.target);
        //for (key9 in g.nodes[tempEdge.target]) {console.log(key9 + " is " + g.nodes[tempEdge.target][key9]);}; //debug
        if (!(validateCPT(tempEdge.target))) {
            // Create the updated CPT
            var cptObj = create_blank_cpt(tempEdge.target);
            // Get the CPT JSON string
            var cptString = create_cpt_form(cptObj);
            //replace the CPT
            $("#cpt_form_"+tempEdge.target).remove();
            $("#cpt"+tempEdge.target).append(cptString);
            $('#cpt_form_'+tempEdge.target).hide();
        };
    };    
}


//Take a node Array
//updates it in the graph (g)
function graphAddNode(nodeArray) {
    var tempNode = {};
    if (g.nodes.hasOwnProperty(nodeArray[1])) {
        //console.log("Node Exists"); //console.log
        tempNode = new node(g.nodes[nodeArray[1]], g.nodes[nodeArray[1]]['attr_array']);
        for (var key in nodeArray[2]) {
            tempNode['attr_array'][key] = nodeArray[2][key];
        }
    } else {
        tempNode = new node(nodeArray[1], nodeArray[2]);        
    };
    //Finally store it back into the graph
    g.nodes[tempNode.id] = tempNode;
    
//    //Debug
//    if (nodeArray[2].hasOwnProperty("CPT")) {
//        for (var key7 in nodeArray[2].CPT) { console.log(key7 + " is " + nodeArray[2].CPT[key7])};
//    }
};

    
//TODO: Finish writing this
//Takes a nodeID
//updates the node table in the HTML
function update_node_table(nodeId) {
    bgColor = "#ffffff";
    var cptObj = {};
    //1. get the node from the graph by nodeID
    //2. create the row for the table
    //2.1 create each cell in the table.
    //2.2 get the CPT from the graph (or fake it)
    //lets make sure the CPT is valid
    var validCPT = validateCPT(nodeId);
    if (validCPT) {
        cptObj = g.nodes[nodeId].attr_array.CPT;
        bgColor = "transparent";
    } else {
        cptObj = create_blank_cpt(nodeId);
        bgColor = "#FF0000";
    };
    
    //2.3 create the CPT form
    var cptString = create_cpt_form(cptObj);
    
    //remove any old rows from the table
    $("#tr"+nodeId).remove();
    
    //add the row back into the table
     $('#Nodes').append("<tr id='tr"+g.nodes[nodeId].id+"'><td>"+g.nodes[nodeId].id+"</td><td class='label'>"+g.nodes[nodeId].attr_array["Label"]+"</td><td>"+g.nodes[nodeId].attr_array["Class"]+"</td><td class='cpt' id='cpt"+g.nodes[nodeId].id+"'>"+cptString+"</td></tr>");
    
    //set the cell background color to indicate constructed CPTs
    $("#cpt"+g.nodes[nodeId].id).css("background-color", bgColor);
    
    //TODO: Make the row hidden.
    $('#cpt_form_'+nodeId).hide();
    
    //sort the table rows
    // https://github.com/padolsey/jQuery-Plugins/blob/master/sortElements/demo.html
    
};
    
    
//Takes a nodeID
//Returns a bool.  True if CPT is valide, false otherwise
//Really just a few checks.  Probably not a complete validation
function validateCPT(nodeId) {
    var valid = true;    
    //console.log("Validating nodeId " + nodeId) //debug
    //Make sure a CPT exists
    if (!(g.nodes[nodeId].attr_array.hasOwnProperty("CPT"))) {
        valid = false;
        //console.log("Node" + nodeId + " didn't have a CPT");  //debug
    //BUG
    //websocket returns a JSON object CPT if CPT came in throgh websocket
    //websocket returns a string CPT if it comes from a saved graph
    //May need to check for which and convert strings to JSON objects before validating
    } else if (typeof g.nodes[nodeId].attr_array["CPT"] == "string") {
        g.nodes[nodeId].attr_array["CPT"] = JSON.parse(g.nodes[nodeId].attr_array["CPT"]);
    //Make sure an index exists
    } else if (!(g.nodes[nodeId].attr_array.CPT.hasOwnProperty("index"))) {
        console.log("NodeId " + nodeId + " has a CPT but no index?"); //debug
        //for (var key6 in g.nodes[nodeId].attr_array.CPT) {console.log(key6 + " is " + g.nodes[nodeId].attr_array.CPT[key6]);};  //Debug
        valid = false;
    } else {
        //If it's a no-parent node, just check for the 0 row.
        if (g.nodes[nodeId].attr_array.CPT.index.length == 2) {
            if (!(0 in g.nodes[nodeId].attr_array.CPT)) {
                valid = false;
                console.log("NodeId " + nodeId + " has no 0 row"); //Debug
            };
        } else {
        // Check to make sure the correct number of parents exist
//            parents = getParents(nodeId);
//            if (parents.length != (g.nodes[nodeId].attr_array.CPT["index"].length -2) ) {
//                valid = false;
//            } else {
                for(var i=0; i < (Math.pow(2, g.nodes[nodeId].attr_array.CPT["index"].length - 2)); i++) {
            //For nodes with parents, check to make sure the correct # of rows exist
                    if (!(i in g.nodes[nodeId].attr_array.CPT)) {
                        valid = false;
                        console.log("NodeId " + nodeId + " has no row " + i); //debug
                    } else {
            //Make sure the row is the right length
                        if (g.nodes[nodeId].attr_array.CPT[i].length != g.nodes[nodeId].attr_array.CPT["index"].length) {
                            valid = false;
                            console.log("NodeId " + nodeId + " has row " + i + " but it's " + g.nodes[nodeId].attr_array.CPT[i].length + " instead of " + g.nodes[nodeId].attr_array.CPT["index"].length);
                            for(var key8 in g.nodes[nodeId].attr_array.CPT["index"]) {console.log(g.nodes[nodeId].attr_array.CPT["index"] + " is " + g.nodes[nodeId].attr_array.CPT["index"][key8]);}; //debug
                        };
                    };
                };
//            };
        };
    };
    //console.log("CPT validated as " + valid); //debug
    return valid;
};


//Takes a nodeID
//Returns a valid CPT object
function create_blank_cpt(nodeId) {
    var node_cpt = new Object();
    var num = null;
    var j = null;
    // get parents
    var parents  = getParents(nodeId);
    
    //Debug
    //console.log("nodeId is " + nodeId + "create_blank_cpt has parents " + parents);
    
    rows = Math.pow(2,parents.length);
    // create header
    node_cpt.nodeId = nodeId;
    node_cpt.index = parents;
    node_cpt.index.push(true,false);
      // for parents^2, create each cpt row
    for (i=0; i < rows; i++) {
      node_cpt[i] = [];
      // for parents
      // create a row with the binary values for the parents, 0 for all trues, 1 for all falses
      num = i;
      j = parents.length - 3;
  
      // convert number to binary in cpt
      while (num > 0) {
        node_cpt[i][j] = num % 2;
        num = (num - node_cpt[i][j]) / 2;
        j--;
      };
      // Fill out the left 0's in the binary
      for (j; j >= 0; j--) {
        node_cpt[i][j] = 0;
      };
      // push 0 true, 1 false;
      node_cpt[i].push(0,1);
    };
    
    return node_cpt;
};

//BUG: If this is run before graph is imported, the edges don't exist in the graph yet so this is wrong
// takes id number of a node
// returns an array of parents in no order
function getParents(node_id) {
    //console.log("node ID is " + node_id);
    parents = [];
    for (var key in g.edges) {
        //console.log(key + " has id " + g.edges[key].id + " source " + g.edges[key].source + " and target " + g.edges[key].target);
        if (g.edges[key].target == node_id) {
            parents.push(g.edges[key].source);
        };
    };
    return parents;
};


//Takes a cptObj
//Returns a string representing the CPT as an input form to be embedded in HTML
function create_cpt_form(cptObj) {
    //Debug
    //for(key in cptObj) {console.log(key + " is " + cptObj[key])};
    // Lets build the CPT form from the CPT object
    var cpt_form = "";
    cpt_form = cpt_form + '<form class="cpt_form" id="cpt_form_'+cptObj.nodeId+'">\n';
    // Build header row
    for (i = 0; i < cptObj.index.length - 2; i++) {
      cpt_form = cpt_form + '<input class="cpt-form" id="cpt_form_p' + cptObj.index[i] + '" value="' + cptObj.index[i] + '" readonly/>';
    }
    cpt_form = cpt_form + '<input class="cpt-form" id="cpt_form_true" value="true" readonly/>';
    cpt_form = cpt_form + '<input class="cpt-form" id="cpt_form_false" value="false" readonly/>';
    cpt_form = cpt_form + '<br />\n';
    // Build CPT rows
    for (i in cptObj) {
      if ((i != "index") && (i != "nodeId")) {
        for (j = 0 ; j < cptObj[i].length - 2 ; j++) {
          //Create the parent binary cells
          cpt_form = cpt_form + '<input class="cpt-form" id="cpt_form_' + i + '.' + j + '" value=' + cptObj[i][j] + ' readonly />';
        }
        //Create the True & False cells
        cpt_form = cpt_form + '<input class="cpt-form" id="cpt_form_' + cptObj.nodeId + "." + i + '.true" value=' + cptObj[i][j] + ' />';
        j++;
        cpt_form = cpt_form + '<input class="cpt-form" id="cpt_form_' + cptObj.nodeId + "." + i + '.false" value=' + cptObj[i][j] + ' />';
        cpt_form = cpt_form + '<br />\n';
      }
    }
    //Add buttons at the bottom
    cpt_form = cpt_form + '<div class="cpt-form-button"><input type="submit" value="AND" class="cpt-form" id="cpt_form_' + cptObj["nodeId"] + '.and_button" onClick="cpt_and('+cptObj["nodeId"]+');" /><input type="submit" value="OR" class="cpt-form" id="cpt_form_' + cptObj["nodeId"] + '.or_button" onClick="cpt_or('+cptObj["nodeId"]+');" /><br />\n';
    cpt_form = cpt_form + '<input type="submit" value=&#x2713; class="cpt-form" id="cpt_form_' + cptObj["nodeId"] + '.save_button" onClick="cpt_save('+cptObj["nodeId"]+');" /><input type="submit" value=&#x2717; class="cpt-form" id="cpt_form_' + cptObj["nodeId"] + '.cancel_button" onClick="cpt_cancel('+cptObj["nodeId"]+');" /><br /></div>\n';
    cpt_form = cpt_form + '</form>\n';
    
    // DEBUG: Log the CPT form so we can see what it is
    //console.log(cpt_form);
    
    return cpt_form;
};


//graphAddNode is probably fine for this.  Probably don't need to recreate it
//function updateNode(eventArray) {
//        var tempNode = {};
//    if (g.nodes.hasOwnProperty(g.nodes[nodeArray[1]])) {
//        tempNode = new node(g.nodes[nodeArray[1]], g.nodes[nodeArray[1]]['attr_array']);
//        for (var key in nodeArray[2]) {
//            tempNode['attr_array'][key] = nodeArray[2][key];
//        }
//    } else {
//        tempNode = new node(nodeArray[1], nodeArray[2]);        
//    };
//    //Finally store it back into the graph
//    g.nodes[tempNode.id] = tempNode;
//};



    
    //takes a nodeId
    //saves the node ID to the websocket (this should cause an event which updates the node in the graph)
    function cpt_save(nodeId) {
        //Get the CPT object
        var cptObj = {};
        var parents = [];
        var validCPT = validateCPT(nodeId);
        if (validCPT) {
            cptObj = g.nodes[nodeId].attr_array.CPT;
        } else {
            cptObj = create_blank_cpt(nodeId);
        };
        
        //for (key5 in cptObj) {console.log(key5 + " is " + cptObj[key5]);}; //Debug
        //console.log(cptObj["index"]);  //debug
        
        // get parents
        parents = cptObj["index"].slice(0);  //slice to get copy of the array
        //remove the last 2 indexes which are 'true' and 'false'
        //for (key6 in parents) {console.log(key6 + " is " + cptObj[key6]);}; //debug
        parents.pop();
        parents.pop();
        
        //iterate through rows
        for (var i=0; i < Math.pow(2, parents.length); i++) {
//            var rowArray = [];
// Not necessary since only the true and false are changing
//            // iterate through columns to build row Array
//            for (var j=0; j < parents.length + 2; j++) {
//                rowArray[j] = $("cpt_form_"+i+"."+j).val();
//            };
            // updat the true and false columns
            cptObj[i][parents.length] = document.getElementById("cpt_form_"+nodeId+"."+i+".true").value;
            j++;
            cptObj[i][parents.length + 1] = document.getElementById("cpt_form_"+nodeId+"."+i+".false").value;
            // save the row
//            cptObj[i] = rowArray;
        };
        
        // Turn the cptObj into a json string
        var cptString = JSON.stringify(cptObj);
        
        // wrap the cpt string
        cptString = '{"cn":{"'+nodeId+'":{"CPT":'+cptString+'}}}';
        
        // send the string to th server
        send(cptString);
    };
    
    
    //takes a nodeId
    //returns the CPT in the table to the one stored in the graph
    function cpt_cancel(nodeId) {
        //recreate the original CPT
        var cptObj = {};
        var validCPT = validateCPT(nodeId);
        if (validCPT) {
            cptObj = g.nodes[nodeId].attr_array.CPT;
        } else {
            cptObj = create_blank_cpt(nodeId);
        };
        // Get the CPT JSON string
        var cptString = create_cpt_form(cptObj);
        // Remove the old cpt
        $("#cpt_form_"+nodeId).remove();
        // Add the new cpt
        $("#cpt"+nodeId).append(cptString);
    };
    
    
    //takes a nodeId
    //updates the CPT in the table to a default "and"
    //a default AND is one that requires all parents to be true
    function cpt_and(nodeId) {
        //Get the CPT object
        var cptObj = {};
        var parents = [];
        var validCPT = validateCPT(nodeId);
        if (validCPT) {
            cptObj = g.nodes[nodeId].attr_array.CPT;
            //console.log("validCPT "+ cptObj['index'] + " and " + g.nodes[nodeId].attr_array.CPT['index']);  //debug
            parents = cptObj["index"].slice(0); //using slide to force a copy of the array
        } else {
            cptObj = create_blank_cpt(nodeId);
            
            //Debug
            //for (key2 in cptObj) {
            //    console.log(key2 + " is " + cptObj[key2]);
            //};
            
            parents = cptObj["index"].slice(0); //using slice to force a copy of the array
        };
        
        //console.log(parents); //Debug
        
        //remove the last 2 indexes which are 'true' and 'false'
        parents.pop();
        parents.pop();
        
        var rows = Math.pow(2, parents.length);
        
        // If there are no parents
        if (parents.length == 0) {
            // Set true to 1
            cptObj[0][0] = 1;
            // set false to 0
            cptObj[0][1] = 0;
        } else {
            // change all lines to false, except the last last one
            for (var i = 0; i < rows - 1; i++)  {
                // Set true to 0
                cptObj[i][parents.length] = 0;
                // Set false to 1
                cptObj[i][parents.length + 1] = 1;
            };
            // Set true to 1
            cptObj[rows - 1][parents.length] = 1;
            // Set false to 0
            cptObj[rows - 1][parents.length +1] = 0;
        };
        
        //for (key4 in cptObj) {console.log(key4 + " is " + cptObj[key4]);};  //Debug
        
        //create the cptString
        var cptString = create_cpt_form(cptObj);
        //update the cpt form int he table
        $("#cpt_form_"+nodeId).remove();
        $("#cpt"+nodeId).append(cptString);

        
    }
    
    
    //takes a nodeId
    //updates the CPT in the table to a default "or"
    //a default OR is one that requires all attribute parents and ANY event/condition parent
    function cpt_or(nodeId) {
        //Get the CPT object
        var cptObj = {};
        var validCPT = validateCPT(nodeId);
        if (validCPT) {
            cptObj = g.nodes[nodeId].attr_array.CPT;
        } else {
            cptObj = create_blank_cpt(nodeId);
        };
        // get parents
        parents = cptObj["index"].slice(0); //slice to get a copy fo the array
        //remove the last 2 indexes which are 'true' and 'false'
        parents.pop();
        parents.pop();
        
        rows = Math.pow(2, parents.length);
        
        // Find columns which represent attributes
        var attributeParents = [];
        for(var i = 0; i < parents.length; i++) {
            //console.log(parents[i] + " is a " + g.nodes[parents[i]].attr_array["Class"]); //debug
            if (g.nodes[parents[i]].attr_array["Class"] == "Attribute") {
                attributeParents.push(i);
            };
        };
        
        //Set the first row to false
        cptObj[0][parents.length] = 0;
        cptObj[0][parents.length + 1] = 1;
        
        // cycle through rows and set all true except those where
        // an attribute is false
        for (var i = 1; i < Math.pow(2, parents.length); i++) {
            //First set the line true
            cptObj[i][parents.length] = 1;
            cptObj[i][parents.length + 1] = 0;
            // For each attribute
            for (var j=0; j < attributeParents.length; j++) {
                //if the attribute column is 0, then set false
                if (cptObj[i][j] == 0) {
                    cptObj[i][parents.length] = 0;
                    cptObj[i][parents.length + 1] = 1;
                };
            };
        };
        
        //create the cptString
        var cptString = create_cpt_form(cptObj);
        //update the cpt form int he table
        $("#cpt_form_"+nodeId).remove();
        $("#cpt"+nodeId).append(cptString);
    };
 

    // Send caught message back on WS
    function send(text){  
        if(text==""){  
          message('Warning: Please enter a message');  
          return ;  
        }  
        try{  
          socket.send(text);  
          addToLog('Sent: '+text)  
        } catch(exception){  
          addToLog('Msg Not Sent');  
        }  
        $('#text').val("");
    };
    
    
    // Takes a nodeID
    // adds the node and it's parents to the canvas
    function canvasIt(nodeId) {
        var parents = [];
        // empty the canvas
        sigInst.emptyGraph();
//        console.log("canvas node id is " + nodeId); //Debug
        // Add the node
        sigInst.addNode(nodeId, {
            Name: nodeId,
            label: nodeId + " - (" + g.nodes[nodeId].attr_array['Class'] + ") - " + g.nodes[nodeId].attr_array['Label'],
            size: 5,
            x: 0.0,
            y: 0.4,
            color: "#000000"
        });
        sigInst.draw();
        
        
        //Get parents
        if (!(g.nodes[nodeId].attr_array.hasOwnProperty("CPT"))) {
            parents = getParents(nodeId);
        } else if (!(validateCPT(nodeId))) {
            parents = getParents(nodeId);
        } else {
            parents = g.nodes[nodeId].attr_array["CPT"]["index"].slice(0);
//            console.log("valid CPT has parents " + parents); //debug
            parents.pop();
            parents.pop(); 
        };
        // add the nodes and edges for parents
        for (var i=0; i < parents.length; i++) {
//            console.log("Parent is " + parents); //debug
            sigInst.addNode(parents[i], {
            Name: parents[i],
            label: parents[i] + " - (" + g.nodes[parents[i]].attr_array['Class'] + ") - " + g.nodes[parents[i]].attr_array['Label'],
            size: 5,
            x: -0.75,
            y: (i/parents.length) * 0.8,
            color: "#00FF00",
            }).addEdge(i,parents[i],nodeId);
        }
        // Draw it
        sigInst.draw();
    }
    
    // takes nothing
    // returns the risks calculated from an attack graph
    function get_risks() {
        // Get the websocket address
        // addressBox.value
//        console.log("WS address is " + addressBox.value)
        // Get the laksis address
        // $("#laksis_address").val()
//        console.log("Laksis address is " + $("#laksis_address".value))
        // request the risks from laksis
        $.post("/get_risks",
            {
                ws_address: addressBox.value,
                laksis_address: $("#laksis_address").val()
            },
            function(data) {
                $("#get_risks").append(data)
            });
    }
