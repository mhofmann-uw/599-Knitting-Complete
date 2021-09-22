"""Tests that generate simple knit graph visualizations"""
from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *


def test_stockinette():
    visualize_knitGraph(stockinette(4, 4))


def test_rib():
    visualize_knitGraph(rib(5, 4, 1))


def test_seed():
    visualize_knitGraph(seed(4, 4))


def test_twisted_stripes():
    visualize_knitGraph(twisted_stripes(4, 5))


def test_lace():
    visualize_knitGraph(lace(4, 4))
