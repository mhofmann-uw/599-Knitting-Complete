from enum import Enum
from typing import Dict, Optional

import networkx

from knit_graphs.Loop import Loop
from knit_graphs.Yarn import Yarn


class Pull_Direction(Enum):
    BtF = "BtF"
    FtB = "FtB"


class KnitGraph:
    def __init__(self):
        # Directed graph for this KnitGraph
        self.graph: networkx.DiGraph = networkx.DiGraph()

        # A map of each unique loop id to its loop
        self.loops: Dict[int, Loop] = {}
        self._last_loop_id: int = -1

        # A list of Yarns used in teh graph
        self.yarns: Dict[str, Yarn] = {}

        # # 2D array layout of all the Loops for this KnitGraph
        # self.rows: Dict[int, List[Loop]] = {}
        #
        # # Index of the last row
        # self.maxRow: int = 0

    def add_loop(self, loop: Loop):
        """
        :param loop: the loop to be added in as a node in the graph
        """
        self.graph.add_node(loop.loop_id, loop=loop)
        assert loop.yarn_id in self.yarns, f"No yarn {loop.yarn_id} in this graph"
        if loop not in self.yarns[loop.yarn_id]:  # make sure the loop is on the yarn specified
            self.yarns[loop.yarn_id].add_loop_to_end(loop_id=None, loop=loop)

    def add_yarn(self, yarn: Yarn):
        """
        :param yarn: the yarn to be added to the graph structure
        """
        self.yarns[yarn.yarn_id] = yarn

    def connect_loops(self, parent_loop_id: int, child_loop_id: int, pull_direction: Pull_Direction = Pull_Direction.BtF, stack_position: Optional[int] = None):
        """
        Creates a stitch-edge by connecting a parent and child loop
        :param parent_loop_id: the id of the parent loop to connect to this child
        :param child_loop_id:  the id of the child loop to connect to the parent
        :param pull_direction: the direction the child is pulled through the parent
        :param stack_position: The position to insert the parent into, by default add on top of the stack
        """
        assert parent_loop_id in self, f"{parent_loop_id} is not in this graph"
        assert child_loop_id in self, f"{child_loop_id} is not in this graph"
        self.graph.add_edge(parent_loop_id, child_loop_id, pull_direction=pull_direction)
        child_loop = self[child_loop_id]
        parent_loop = self[parent_loop_id]
        child_loop.add_parent_loop(parent_loop, stack_position)

    def __contains__(self, item):
        """
        :param item: the loop being checked for in the graph
        :return: true if the loop_id of item or the loop is in the graph
        """
        if type(item) is int:
            return self.graph.has_node(item)
        elif isinstance(item, Loop):
            return self.graph.has_node(item.loop_id)
        else:
            return False

    def __getitem__(self, item: int) -> Loop:
        """
        :param item: the loop_id being checked for in the graph
        :return: the Loop in the graph with the matching id
        """
        if item not in self:
            raise AttributeError
        else:
            return self.graph.nodes[item]["loop"]


def create_stst_knit_graph(width: int = 4, height: int = 4) -> KnitGraph:
    knitGraph = KnitGraph()
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
