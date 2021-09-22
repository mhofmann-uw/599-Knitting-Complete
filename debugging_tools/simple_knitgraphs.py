"""Simple knitgraph generators used primarily for debugging"""
from knit_graphs.Knit_Graph import Knit_Graph, Pull_Direction
from knit_graphs.Yarn import Yarn


def stockinette(width: int = 4, height: int = 4) -> Knit_Graph:
    """
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: a knitgraph of stockinette on one yarn of width stitches by height course
    """
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn")
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    for _ in range(1, height):
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(child)
            knitGraph.connect_loops(parent_id, child_id)
        prior_row = next_row

    return knitGraph


def rib(width: int = 4, height: int = 4, rib_width: int = 1) -> Knit_Graph:
    """
    :param rib_width: determines how many columns of knits and purls are in a single rib.
    (i.e.) the first course of width=4 and rib_width=2 will be kkpp. Always start with knit columns
    :param width: a number greater than 0 to set the number of stitches in the swatch
    :param height: A number greater than 2 to set the number of courses in the swatch
    :return: A knit graph with a repeating columns of knits (back to front) then purls (front to back).
    """
    assert width > 0
    assert height > 1
    assert rib_width <= width

    knitGraph = Knit_Graph()
    yarn = Yarn("yarn")
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    next_row = []
    for column, parent_id in enumerate(reversed(prior_row)):
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knitGraph.add_loop(child)
        rib_id = column / rib_width
        if rib_id % 2 == 0:  # even ribs:
            pull_direction = Pull_Direction.BtF
        else:
            pull_direction = Pull_Direction.FtB
        knitGraph.connect_loops(parent_id, child_id, pull_direction=pull_direction)

    for _ in range(2, height):
        prior_row = next_row
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(child)
            grand_parent = [*knitGraph.graph.predecessors(parent_id)][0]
            parent_pull_direction = knitGraph.graph[grand_parent][parent_id]["pull_direction"]
            knitGraph.connect_loops(parent_id, child_id, pull_direction=parent_pull_direction)

    return knitGraph


def seed(width: int = 4, height=4) -> Knit_Graph:
    """
    :param width: a number greater than 0 to set the number of stitches in the swatch
    :param height: A number greater than 0 to set teh number of courses in the swatch
    :return: A knit graph with a checkered pattern of knit and purl stitches of width and height size.
    The first stitch should be a knit
    """
    assert width > 0
    assert height > 1

    knitGraph = Knit_Graph()
    yarn = Yarn("yarn")
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    prior_row = first_row
    next_row = []
    for column, parent_id in enumerate(reversed(prior_row)):
        child_id, child = yarn.add_loop_to_end()
        next_row.append(child_id)
        knitGraph.add_loop(child)
        if column % 2 == 0:  # even seed:
            pull_direction = Pull_Direction.BtF
        else:
            pull_direction = Pull_Direction.FtB
        knitGraph.connect_loops(parent_id, child_id, pull_direction=pull_direction)

    for _ in range(2, height):
        prior_row = next_row
        next_row = []
        for parent_id in reversed(prior_row):
            child_id, child = yarn.add_loop_to_end()
            next_row.append(child_id)
            knitGraph.add_loop(child)
            grand_parent = [*knitGraph.graph.predecessors(parent_id)][0]
            parent_pull_direction = knitGraph.graph[grand_parent][parent_id]["pull_direction"]
            knitGraph.connect_loops(parent_id, child_id, pull_direction=parent_pull_direction.opposite())

    return knitGraph


def twisted_stripes(width: int = 4, height=5, left_twists: bool = True) -> Knit_Graph:
    """
    :param left_twists: if True, make the left leaning stitches in front, otherwise right leaning stitches in front
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: A knitgraph with repeating pattern of twisted stitches surrounded by knit wales
    """
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn")
    knitGraph.add_yarn(yarn)

    # Add the first course of loops
    first_course = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_course.append(loop_id)
        knitGraph.add_loop(loop)

    def add_loop_and_knit(p_id, depth=0, parent_offset: int = 0):
        """
        adds a loop by knitting to the knitgraph
        :param parent_offset: Set the offset of the parent loop in the cable. offset = parent_index - child_index
        :param p_id: the parent loop's id
        :param depth: the crossing- depth to knit at
        """
        child_id, child = yarn.add_loop_to_end()
        next_course.append(child_id)
        knitGraph.add_loop(child)
        knitGraph.connect_loops(p_id, child_id, depth=depth, parent_offset=parent_offset)

    if left_twists:  # set the depth for the first loop in the twist (1 means it will cross in front of other stitches)
        twist_depth = 1
    else:
        twist_depth = -2

    # add new courses
    prior_course = first_course
    for course in range(1, height):
        next_course = []
        reversed_prior_course = [*reversed(prior_course)]
        for col, parent_id in enumerate(reversed_prior_course):
            if course % 2 == 0 or col % 4 == 0 or col % 4 == 3:  # knit on even rows and before and after twists
                add_loop_and_knit(parent_id)
            elif col % 4 == 1:
                next_parent_id = reversed_prior_course[col + 1]
                add_loop_and_knit(next_parent_id, twist_depth, -1)
                twist_depth = -1 * twist_depth  # switch depth for neighbor
            elif col % 4 == 2:
                next_parent_id = reversed_prior_course[col - 1]
                add_loop_and_knit(next_parent_id, twist_depth, 1)
                twist_depth = -1 * twist_depth  # switch depth for next twist
        prior_course = next_course

    return knitGraph


# def twisted_stripes(width: int = 4, height=5) -> Knit_Graph:
#     """
#     :param width: the number of stitches of the swatch
#     :param height:  the number of courses of the swatch
#     :return: A knitgraph with repeating pattern of twisted stitches surrounded by knit wales
#     """
#     knitGraph = Knit_Graph()
#     yarn = Yarn("yarn")
#     knitGraph.add_yarn(yarn)
#     first_row = []
#     for _ in range(0, width):
#         loop_id, loop = yarn.add_loop_to_end()
#         first_row.append(loop_id)
#         knitGraph.add_loop(loop)
#
#     def add_loop_and_knit(p_id, depth=0):
#         """
#         adds a loop by knitting to the knitgraph
#         :param p_id: the parent loop's id
#         :param depth: the crossing- depth to knit at
#         """
#         child_id, child = yarn.add_loop_to_end()
#         next_row.append(child_id)
#         knitGraph.add_loop(child)
#         knitGraph.connect_loops(p_id, child_id, depth=depth)
#
#     prior_row = first_row
#     first_depth = 1  # switch between left and right twists
#     for row in range(1, height):
#         next_row = []
#         prior_parent_id = -1
#         reversed_prior_row = [*reversed(prior_row)]
#         for col, parent_id in enumerate(reversed_prior_row):
#             if row % 2 == 0 or col % 4 == 0 or col % 4 == 3:  # knit on even rows and before and after twists
#                 add_loop_and_knit(parent_id)
#             elif col % 4 == 1:
#                 prior_parent_id = parent_id
#                 next_parent_id = reversed_prior_row[col + 1]
#                 add_loop_and_knit(next_parent_id, first_depth)  # set to opposite depth of crossing partner
#             elif col % 4 == 2:
#                 add_loop_and_knit(prior_parent_id, -1 * first_depth)  # set to opposite depth of crossing partner
#                 first_depth = -1 * first_depth  # switch depth for next twist course
#         prior_row = next_row
#
#     return knitGraph


def lace(width: int = 4, height: int = 4):
    """
    :param width: the number of stitches of the swatch
    :param height:  the number of courses of the swatch
    :return: a knitgraph with k2togs and yarn-overs surrounded by knit wales
    """
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn")
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    def add_loop_and_knit(p_id):
        """
        Knits a loop into the graph
        :param p_id: the id of the parent loop being knit through
        :return: the id of the child loop created
        """
        c_id, c = yarn.add_loop_to_end()
        next_row.append(c_id)
        knitGraph.add_loop(c)
        knitGraph.connect_loops(p_id, c_id)
        return c_id

    prior_row = first_row
    for row in range(1, height):
        next_row = []
        prior_parent_id = -1
        reversed_prior_row = [*reversed(prior_row)]
        for col, parent_id in enumerate(reversed_prior_row):
            if row % 2 == 0 or col % 4 == 0 or col % 4 == 3:  # knit on even rows and before and after twists
                add_loop_and_knit(parent_id)
            elif col % 4 == 1:
                child_id, child = yarn.add_loop_to_end()
                knitGraph.add_loop(child)
                next_row.append(child_id)  # yarn over
                prior_parent_id = parent_id
            elif col % 4 == 2:
                child_id = add_loop_and_knit(parent_id)
                knitGraph.connect_loops(prior_parent_id, child_id)
        prior_row = next_row

    return knitGraph


def lace_and_twist():
    width = 13
    knitGraph = Knit_Graph()
    yarn = Yarn("yarn")
    knitGraph.add_yarn(yarn)
    first_row = []
    for _ in range(0, width):
        loop_id, loop = yarn.add_loop_to_end()
        first_row.append(loop_id)
        knitGraph.add_loop(loop)

    next_row = []
    for _ in range(0, width):
        child_id, child = yarn.add_loop_to_end()
        knitGraph.add_loop(child)
        next_row.append(child_id)
    # knit edge
    knitGraph.connect_loops(0, 25)
    knitGraph.connect_loops(12, 13)
    # bottom of decrease stack
    knitGraph.connect_loops(1, 24, stack_position=0)
    knitGraph.connect_loops(6, 19, stack_position=0)
    knitGraph.connect_loops(11, 14, stack_position=0)
    # 2nd of decrease stack
    knitGraph.connect_loops(2, 24, stack_position=1, parent_offset=1)
    knitGraph.connect_loops(5, 19, stack_position=1, parent_offset=-1)
    knitGraph.connect_loops(10, 14, stack_position=1, parent_offset=-1)
    # 3rd of decrease stack
    knitGraph.connect_loops(7, 19, stack_position=2, parent_offset=1)
    # twist  right
    knitGraph.connect_loops(3, 21, depth=1, parent_offset=1)
    knitGraph.connect_loops(4, 22, depth=-1, parent_offset=-1)
    # twist left
    knitGraph.connect_loops(8, 16, depth=-1, parent_offset=1)
    knitGraph.connect_loops(9, 17, depth=1, parent_offset=-1)

    for parent_id in reversed(next_row):
        child_id, child = yarn.add_loop_to_end()
        knitGraph.add_loop(child)
        knitGraph.connect_loops(parent_id, child_id)

    return knitGraph
