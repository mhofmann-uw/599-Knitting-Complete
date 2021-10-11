"""Tests that generate simple knit graph visualizations"""
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *


def test_stockinette():
    visualize_knitGraph(stockinette(4, 4))


def test_rib():
    visualize_knitGraph(rib(6, 6, 2))


def test_seed():
    visualize_knitGraph(seed(4, 4))


def test_twisted_stripes():
    visualize_knitGraph(twisted_stripes(8, 5))


def test_lace():
    visualize_knitGraph(lace(4, 4))


if __name__ == "__main__":
    test_stockinette()
    test_rib()
    test_seed()
    test_twisted_stripes()
    test_lace()


def test_short_rows():
    knit_graph = short_rows(6, buffer_height=1)
    _, __ = knit_graph.get_courses()
    visualize_knitGraph(knit_graph)
