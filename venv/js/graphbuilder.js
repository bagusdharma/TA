function renderGraph(nodesJson, edgesJson){
  console.log(nodesJson);
  console.log(edgesJson);
  // create an array with nodes
  var nodes = new vis.DataSet(nodesJson);

  // create an array with edges
  var edges = new vis.DataSet(edgesJson);

  // create a network
  var container = document.getElementById('mynetwork');

  // provide the data in the vis format
  var data = {
    nodes: nodes,
    edges: edges
  };
  var options = {
    groups: {
        failure: {
            color: {
                background: 'red'
            }
        },
        state: {
            color: {
                background: 'lime'
            }
        },
        startstate: {
            font: {
                size: 12,
                color: 'white'
            },
            color: {
                background: 'blueviolet'
            }
        },
        finalstate: {
            font: {
                size: 12,
                color: 'white'
            },
            color: {
                background: 'blue'
            }
        }
    },
    edges: {
        arrows: {
            to: {
                enabled: true
            }
        },
        smooth: {
            enabled: false,
            type: 'continuous'
        }
    },
    physics: {
        adaptiveTimestep: true,
        barnesHut: {
            gravitationalConstant: -8000,
            springConstant: 0.04,
            springLength: 95
        },
        stabilization: {
            iterations: 2000
        }
    },
    layout: {
        randomSeed: 5,
        improvedLayout: true,
        hierarchical: {
          enabled: true,
          sortMethod: 'directed'
        }
    }
};

  // initialize your network!
  var network = new vis.Network(container, data, options);
}
