from typing import Tuple, Dict, List

from knit_graphs.Knit_Graph import Knit_Graph

MAX_LAYERS = 3

class Knit_Layer:

    def __init__(self, knit_graph: Knit_Graph, position: int = 0):
        assert position >=0, "Positions are positive, with the front at the lowest value (0)"
        assert position < MAX_LAYERS, f"Greater than 1/{MAX_LAYERS} Gauging is not accepted"
        self.position = position
        self.knit_graph = knit_graph

    def get_courses(self) -> Tuple[Dict[int, int], Dict[int, List[int]]]:
        """
        :return: The course structure for the layer's knitgraph
        """
        return self.knit_graph.get_courses()


