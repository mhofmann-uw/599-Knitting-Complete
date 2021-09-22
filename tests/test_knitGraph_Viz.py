from knit_graphs.knitgraph_generators import *
from knit_graphs.knitGraph_Viz import visualize_knitGraph


def test_visualize_knit_graph():
    knitGraph = stockinette()
    visualize_knitGraph(knitGraph)


def test_twist_knitGraph():
    knitGraph = twisted_stripes()
    visualize_knitGraph(knitGraph)


def test_lace():
    knitGraph = lace()
    visualize_knitGraph(knitGraph)


def test_lace_and_twist():
    knitGraph = lace_and_twist()
    visualize_knitGraph(knitGraph)