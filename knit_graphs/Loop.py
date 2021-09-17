import json
from typing import List, Optional


class Loop:
    def __init__(self, loop_id: int, yarn_id: str, is_twisted: bool = False):
        """
        :param loop_id: id of loop. IDs should represent the order that loops are created with the first loop being created with id 0
        :param is_twisted: True if the loop should be twisted (created by pulling a carrier backwards across the needle)
        """
        self.is_twisted = is_twisted
        # self.course = course
        # self.index_in_course = index_in_course
        assert loop_id >= 0, f"{loop_id}: Loop_id must be non-negative"
        self._loop_id: int = loop_id
        self.yarn_id = yarn_id
        # the list of loops that this loop is pulled through. The order in the list implies the stacking order with the first loop at the bottom the stack
        self.parent_loops: List[Loop] = []
        # self.planeDeformationByChildren = None
        # self.planeDeformationByParents = None
        # self.curvature = None
        # self.waleDeformation = None
        # self.waleCompression = None
        # self.maxWaleDepth = None
        # self.loopParams = {}

    def add_parent_loop(self, parent, stack_position: Optional[int] = None):
        """
        Adds the parent Loop onto the stack of parent_loops.
        :param parent: the Loop to be added onto the stack
        :param stack_position: The position to insert the parent into, by default add on top of the stack
        """
        if stack_position is not None:
            self.parent_loops.insert(stack_position, parent)
        else:
            self.parent_loops.append(parent)

    @property
    def loop_id(self) -> int:
        return self._loop_id

    # @property
    # def course(self) -> int:
    #     return self._row
    #
    # @course.setter
    # def course(self, row: int):
    #     assert row >= -1, f"{row}: Cannot be at row below cast on (-1)"
    #     self._row: int = row

    # @property
    # def index_in_course(self) -> int:
    #     return self._index_in_row
    #
    # @index_in_course.setter
    # def index_in_course(self, index_in_row: int):
    #     assert index_in_row >= 0, f"{index_in_row}: Cannot be at negative in-row index"
    #     self._index_in_row: int = index_in_row

    @property
    def is_twisted(self) -> bool:
        return self._is_twisted

    @is_twisted.setter
    def is_twisted(self, is_twisted: bool):
        self._is_twisted = is_twisted

    @property
    def yarn_id(self) -> str:
        return self._yarn_id

    @yarn_id.setter
    def yarn_id(self, yarn_id: str):
        self._yarn_id: str = yarn_id

    def __hash__(self):
        return self.loop_id

    def __eq__(self, other):
        return isinstance(other, Loop) and self.loop_id == other.loop_id and self.yarn_id == other.yarn_id

    def __lt__(self, other):
        assert isinstance(other, Loop)
        return self.loop_id < other.loop_id

    def __gt__(self, other):
        assert isinstance(other, Loop)
        return self.loop_id > other.loop_id

    def __str__(self):
        if self.is_twisted:
            twisted = ", twisted"
        else:
            twisted = ""
        return f"{self.loop_id} on yarn {self.loop_id}{twisted}"

    def __repr__(self):
        return str(self)

