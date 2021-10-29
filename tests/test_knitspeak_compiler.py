from debugging_tools.knit_graph_viz import visualize_knitGraph

from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler


def test_stst():
    pattern = "all rs rows k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 4, pattern)
    visualize_knitGraph(knit_graph, "stst.html")


def test_rib():
    rib_width = 2
    pattern = f"all rs rows k rib={rib_width}, p rib. all ws rows k rib, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 4, pattern)
    visualize_knitGraph(knit_graph, "rib.html")


def test_cable():
    pattern = r"""
        1st row k, lc2|2, k, rc2|2, [k] to end.
        all ws rows p.
        3rd row k 2, lc2|1, k, rc1|2, [k] to end.
        5th row k 3, lc1|1, k, rc1|1, [k] to end.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(11, 6, pattern)
    visualize_knitGraph(knit_graph, "cables.html")

def test_twist():
    pattern = "all rs rows k, lc1|1, k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 2, pattern)
    visualize_knitGraph(knit_graph, "cables.html")

def test_lace():
    pattern = r"""
        all rs rows k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
        all ws rows p 2, k, p 3, k, p 2.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(9, 6, pattern)
    visualize_knitGraph(knit_graph, "lace.html")

def test_small_lace():
    pattern = "all rs rows k, k2tog, yo, k. all ws rows p."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 2, pattern)
    visualize_knitGraph(knit_graph, "lace.html")


def test_write_slipped_rib():
    rib_width = 1
    pattern = f"all rs rows k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rows k rib, [slip rib, k rib] to last rib sts, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(6, 3, pattern)
    visualize_knitGraph(knit_graph, "slipped_rib.html")


if __name__ == "__main__":
    test_stst()
    test_rib()
    test_write_slipped_rib()
    test_cable()
    test_lace()
