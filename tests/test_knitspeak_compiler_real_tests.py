from debugging_tools.knit_graph_viz import visualize_knitGraph
from knitspeak_compiler.knitspeak_compiler import Knitspeak_Compiler


def test_row_closures():
    pattern = r"""from rs 1 to ((1+n=5)/2) rows k border=currow, [p] to last border sts, k border.
from ws 1 to ((1+n)/2)rows p border=currow, [k] to last border sts, p border."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(7, 3, pattern)
    visualize_knitGraph(knit_graph, "triangle.html")


def test_compile():
    pattern = r"""from 1st to 4th row [k, p] to last st, k."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "stst_4x4.html")


def test_stitches():
    pattern = r"""1st row k, LC1|2P, [k] to end. 2nd row p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "cable.html")


def test_decrease():
    pattern = r"""all rs rows k, k2tog, yo, [k] to end. all ws rows p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "k2tog.html")
    pattern = r"""all rs rows k, k3tog, yo, yo, [k] to end. all ws rows p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "k3tog.html")
    pattern = r"""all rs rows k, yo, skpo, [k] to end. all ws rows p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "skpo.html")
    pattern = r"""all rs rows k, yo, yo, s2kpo, [k] to end. all ws rows p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "s2kpo.html")
    pattern = r"""all rs rows k, yo, sk2po,yo, [k] to end. all ws rows p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(5, 4, pattern)
    visualize_knitGraph(knit_graph, "sk2po.html")


def test_slip():
    pattern = r"""1st row slip, k 2, slip. from 2nd to 4th row p."""
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 4, pattern)
    visualize_knitGraph(knit_graph, "slip.html")


def test_side_defs():
    pattern = r"""1st and 5th row k 2, p 2. flipped all ws rows p. 3rd row k, p, k, p. """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 7, pattern)
    visualize_knitGraph(knit_graph, "purlWS.html")


def test_num_var():
    rib = 1
    pattern = f"all rs rows k rib={rib}, p rib. flipped all ws rows k rib, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(4, 4, pattern)
    visualize_knitGraph(knit_graph, "purlWS.html")


#assignment tests:

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
        3rd row k 2, lc2|1p, k, rc1p|2, [k] to end.
        5th row k 3, lc1p|1p, k, rc1p|1p, [k] to end.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(11, 6, pattern)
    visualize_knitGraph(knit_graph, "cables.html")


def test_lace():
    pattern = r"""
        all rs rows k, k2tog, yo 2, sk2po, yo 2, skpo, k. 
        all ws rows p 2, k, p 3, k, p 2.
    """
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(9, 6, pattern)
    visualize_knitGraph(knit_graph, "lace.html")


def test_write_slipped_rib():
    rib_width = 1
    pattern = f"all rs rows k rib={rib_width}, [k rib, p rib] to last rib sts, k rib. all ws rows k rib, [slip rib, k rib] to last rib sts, p rib."
    compiler = Knitspeak_Compiler()
    knit_graph = compiler.compile(6,3, pattern)
    visualize_knitGraph(knit_graph, "slipped_rib.html")
