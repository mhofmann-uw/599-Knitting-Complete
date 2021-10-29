from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitting_machine.knitgraph_to_knitout import Knitout_Generator


def test_stst():
    knitGraph = stockinette(20, 10)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_stst.k")


def test_rib():
    knitGraph = rib(20, 10, 2)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_rib2.k")


def test_seed():
    knitGraph = seed(20, 10)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_seed.k")


def test_lace():
    knitGraph = lace(4,4)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_lace.k")


def test_both_twists():
    knitGraph = both_twists(height=3)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_twists.k")


def test_write_shortrows():
    knitGraph = short_rows(20, buffer_height=5)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_short_rows.k")
