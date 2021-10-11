from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitting_machine.knitgraph_to_knitout import Knitout_Generator



def test_lace_twist():
    knitGraph = lace_and_twist()
    visualize_knitGraph(knitGraph)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_lace_twist.k")


def test_stst():
    knitGraph = stockinette(20, 20)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_stst.k")


def test_rib():
    knitGraph = rib(20, 20, 2)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_rib2.k")


def test_seed():
    knitGraph = seed(20, 20)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_seed.k")


def test_lace():
    knitGraph = lace(20, 20)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_lace.k")


def test_left_twists():
    knitGraph = twisted_stripes(4, 4, True)
    visualize_knitGraph(knitGraph)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_leftTwists.k")


def test_right_twists():
    knitGraph = twisted_stripes(20, 20, False)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_rightTwists.k")


def test_write_shortrows():
    knitGraph = short_rows(20, buffer_height=5)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test_short_rows.k")
