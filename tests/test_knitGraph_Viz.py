from knit_graphs.KnitGraph import create_stst_knit_graph
from knit_graphs.knitGraph_Viz import visualize_knitGraph


def test_visualize_knit_graph():
    knitGraph = create_stst_knit_graph()
    visualize_knitGraph(knitGraph)
