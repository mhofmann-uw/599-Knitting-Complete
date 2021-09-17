from typing import Dict

from pyvis.options import Layout

from knit_graphs.KnitGraph import KnitGraph
from pyvis import network as nw


def visualize_knitGraph(knitGraph: KnitGraph):
    # layout = Layout()
    # layout.hierarchical.enabled = True
    # layout.hierarchical.direction = "DU"
    # layout.hierarchical.sortMethod = "directed"
    # layout.hierarchical.parentCentralization = False
    # options = nw.Options(layout=layout)
    # options.layout.improvedLayout = False
    # options.physics.enabled=False
    network = nw.Network('500px', '500px', layout=True)
    network.options.layout.hierarchical.enabled = True
    network.options.layout.hierarchical.direction = "UD"
    network.options.layout.hierarchical.sortMethod = "directed"
    network.options.layout.hierarchical.parentCentralization = False
    network.options.layout.improvedLayout = False
    network.options.physics.enabled = False
    node_to_level: Dict[int, int] = {}
    for node in knitGraph.graph.nodes:
        predecessors = [*knitGraph.graph.predecessors(node)]
        if len(predecessors) == 0:  # loop with no parents
            node_to_level[node] = 0
        else:  # has a parent edge
            parent_id = predecessors[0]
            parent_level = node_to_level[parent_id]
            node_to_level[node] = parent_level + 1

    top_level = max(*node_to_level.values())
    for node in knitGraph.graph.nodes:
        network.add_node(node, label=str(node), level=top_level - node_to_level[node])

    for yarn in knitGraph.yarns.values():
        for prior_node, next_node in yarn.yarn_graph.edges:
            if not knitGraph.graph.has_edge(prior_node, next_node):  # there is a stitch between these to yarn connected loops
                network.add_edge(prior_node,next_node, weight=1, arrow="middle", physics=False)

    for parent_id, child_id in knitGraph.graph.edges:
        direction = knitGraph.graph[parent_id][child_id]["pull_direction"]
        network.add_edge(parent_id, child_id, arrows="middle", label=direction.value, weight=2, physics=False)

    network.show_buttons()
    network.show('nx.html')
