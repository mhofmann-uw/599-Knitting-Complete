"""A method for visualizing KnitGraphs as a graph structure, mostly for debugging"""
from pyvis import network as nw

from knit_graphs.KnitGraph import KnitGraph


def visualize_knitGraph(knitGraph: KnitGraph, height: float = 750, width: float = 1000):
    """
    Runs an html file in browser to visualize the given knitgraph
    :param knitGraph: the KnitGraph to visualize
    :param height: the height of the html window
    :param width: the width of the html window
    """
    network = nw.Network(f'{height}px', f'{width}px', layout=True, directed=True)
    network.options.layout.hierarchical.enabled = True
    network.options.layout.hierarchical.direction = "LR"  # make the stitches start at the bottom
    network.options.layout.hierarchical.sortMethod = "hubsize"
    loop_ids_to_course, course_to_loop_ids = knitGraph.get_courses()
    max_node = max(*knitGraph.loops.keys())
    for node in knitGraph.graph.nodes:
        course = loop_ids_to_course[node]
        loops_in_course = course_to_loop_ids[course]
        if course % 2 != 0:
            loops_in_course = [*reversed(loops_in_course)]
        pos_in_course = loops_in_course.index(node)
        network.add_node(node, label=str(node), value=node, shape="circle", level=pos_in_course, physics=True)

    for yarn in knitGraph.yarns.values():
        for prior_node, next_node in yarn.yarn_graph.edges:
            network.add_edge(prior_node, next_node, arrow="middle", physics=True)

    for parent_id, child_id in knitGraph.graph.edges:
        direction = knitGraph.graph[parent_id][child_id]["pull_direction"]
        network.add_edge(child_id, parent_id, arrows="middle", label=direction.value, physics=True)

    network.show_buttons(filter_=["physics"]) # turn on to show different control windows, see pyVis documentation
    network.show('nx.html')
