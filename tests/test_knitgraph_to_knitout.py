from debugging_tools.knit_graph_viz import visualize_knitGraph
from debugging_tools.simple_knitgraphs import *
from knitting_machine.Machine_State import Pass_Direction
from knitting_machine.knitgraph_to_knitout import Knitout_Generator


def test_cast_on():
    knitGraph = stockinette(width=4, height=4)
    visualize_knitGraph(knitGraph)
    generator = Knitout_Generator(knitGraph)
    generator._cast_on()
    for instruction in generator._instructions:
        print(instruction)


def test__find_target_needles():
    knitGraph = lace_and_twist()
    visualize_knitGraph(knitGraph)
    generator = Knitout_Generator(knitGraph)
    generator._cast_on()
    results = generator._find_target_needles(generator._courses_to_loop_ids[1.0], Pass_Direction.Right_to_Left)
    print(results)


def test__do_xfers():
    knitGraph = lace_and_twist()
    visualize_knitGraph(knitGraph)
    generator = Knitout_Generator(knitGraph)
    generator._cast_on()
    generator._knit_row(generator._courses_to_loop_ids[1.0], Pass_Direction.Right_to_Left)
    generator.write_instructions("test.k")


def test_write_instructions():
    knitGraph = lace_and_twist()
    visualize_knitGraph(knitGraph)
    generator = Knitout_Generator(knitGraph)
    generator.write_instructions("test.k")
