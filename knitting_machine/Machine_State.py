"""The class structures used to maintain the machine state"""
from enum import Enum
from typing import Optional, List, Tuple, Dict, Set

from knitting_machine.needles import Needle, Slider_Needle
from knitting_machine.yarn_carrier import Yarn_Carrier


class Pass_Direction(Enum):
    """
    An enumerator for the two directions the carriage can pass on the machine
    Needles are oriented on the machine left to right in ascending order:
    Left -> 0 1 2 ... N <- Right
    """
    Right_to_Left = "-"
    Left_to_Right = "+"

    def opposite(self):
        """
        :return: the opposite pass direction of this
        """
        if self.value == Pass_Direction.Right_to_Left.value:
            return Pass_Direction.Left_to_Right
        else:
            return Pass_Direction.Right_to_Left

    def next_needle_position(self, needle_pos: int):
        """
        :param needle_pos: the needle that we are looking for the next neighbor of
        :return: the next needle position in the pass direction
        """
        if self.value == Pass_Direction.Right_to_Left.value:
            return needle_pos - 1
        else:
            return needle_pos + 1

    def prior_needle_position(self, needle_pos: int):
        """
        :param needle_pos: the needle that we are looking for the prior neighbor of
        :return: the prior needle position in the pass direction
        """
        if self.value == Pass_Direction.Right_to_Left.value:
            return needle_pos + 1
        else:
            return needle_pos - 1

    def __str__(self):
        return self.value


class Machine_Bed:
    """
    A structure to hold information about loops held on one bed of needles...

    Attributes
    ----------
    held_loops : Dict[int, List[int]
        a dictionary keyed by needle positions to the stack of loops on the needle
    loops_to_needle: Dict[int, Optional[int]]
        A dictionary keyed by loop ids to the needle location that this loop is currently held at.
         If it is not held this is None or non-existent
    """

    def __init__(self, is_front: bool, needle_count: int = 250):
        """
        A representation of the state of a bed on the machine
        :param is_front: True if this is the front bed, false if it is the back bed
        :param needle_count: the number of needles that are on this bed
        """
        self._is_front: bool = is_front
        self._needle_count: int = needle_count
        self.held_loops: Dict[int, List[int]] = {i: [] for i in range(0, self.needle_count)}  # increasing indices indicate needles moving from left to right
        # i.e., LEFT -> 0 1 2....N <- RIGHT of Machine
        self.held_slider_loops: Dict[int, List[int]] = {i: [] for i in range(0, self.needle_count)}
        self.loops_to_needle: Dict[int, Optional[int]] = {}
        self.loops_to_slider_needle: Dict[int, Optional[int]] = {}

    @property
    def needle_count(self) -> int:
        """
        :return: the number of needles on the bed
        """
        return self._needle_count

    def __len__(self):
        return self.needle_count

    @property
    def is_front(self) -> bool:
        """
        :return: true if this is the front bed
        """
        return self._is_front

    def add_loop(self, loop_id: Optional[int], needle: Needle, drop_prior_loops: bool = True):
        """
        Puts the loop_id on given needle, overrides existing loops as if a knit operation took place
        :param needle:
        :param drop_prior_loops: If true, any loops currently held on this needle are dropped
        :param loop_id: the loop_id to be held on the needle
        """
        assert 0 <= needle.position < self.needle_count, f"Cannot place a loop at position {needle.position}"
        assert not (drop_prior_loops and needle.is_slider), "Cannot knit on slider needle"
        if drop_prior_loops:
            self.drop_loop(needle.position)
        if not needle.is_slider:
            self.held_loops[needle.position].append(loop_id)
            self.loops_to_needle[loop_id] = needle.position
        else:
            self.held_slider_loops[needle.position].append(loop_id)
            self.loops_to_slider_needle[loop_id] = needle.position

    def drop_loop(self, needle_position: int):
        """
        Clears the loops held at this position as though a drop operation has been done
        :param needle_position: The position to drop loops from main and slider needles
        """
        assert 0 <= needle_position < self.needle_count, f"Cannot drop a loop at position {needle_position}"
        current_loops = self.held_loops[needle_position]
        self.held_loops[needle_position] = []
        for loop in current_loops:
            self.loops_to_needle[loop] = None
        current_loops = self.held_slider_loops[needle_position]
        self.held_slider_loops[needle_position] = []
        for loop in current_loops:
            self.loops_to_slider_needle[loop] = None

    def __getitem__(self, item: Needle) -> List[int]:
        """
        :param item: the needle position to get a loop from
        :return: the loop_id held at that position
        """
        if item.is_slider:
            return self.held_slider_loops[item.position]
        else:
            return self.held_loops[item.position]

    def get_needle_of_loop(self, loop_id: int) -> Optional[Needle]:
        """
        :param loop_id: the loop being searched for
        :return: None if the bed does not hold the loop, otherwise the needle position that holds it
        """
        if loop_id not in self.loops_to_needle:
            if loop_id not in self.loops_to_slider_needle:
                return None
            else:
                return Slider_Needle(self.is_front, self.loops_to_slider_needle[loop_id])
        return Needle(self.is_front, self.loops_to_needle[loop_id])


class Machine_State:
    """
    The current state of a whole V-bed knitting machine
    ...

    Attributes
    ----------
    racking: int
        The current racking of the machine: R = f-b
    front_bed: Machine_Bed
        The status of needles on the front bed
    back_bed: Machine_Bed
        The status of needles on the back bed
    last_carriage_direction: Pass_Direction
        the last direction the carriage took, used to infer the current position of the carriage (left or right)
    in_hooks: Set[knitting_machine.yarn_carrier.Yarn_Carrier]
        The set of yarn carriers that are currently hooked on the machine and active
    yarns_in_operation: Set[knitting_machine.yarn_carrier.Yarn_Carrier]
        The current yarns that being knit with and have not been cut, may also be hooked
    """

    def __init__(self, needle_count: int = 250, racking: float = 0):
        """
        Maintains the state of the machine
        :param needle_count:the number of needles that are on this bed
        :param racking:the current racking between the front and back bed: r=f-b
        """
        self.racking: float = racking
        self.front_bed: Machine_Bed = Machine_Bed(is_front=True, needle_count=needle_count)
        self.back_bed: Machine_Bed = Machine_Bed(is_front=False, needle_count=needle_count)
        self.last_carriage_direction: Pass_Direction = Pass_Direction.Left_to_Right
        # Presumes carriage is left on Right side before knitting
        self.in_hooks: Set[Yarn_Carrier] = set()
        self.yarns_in_operation: Set[Yarn_Carrier] = set()
        self.carriage_passes = []
        self.instructions = [";!knitout-2\n",
                             ";;Machine: SWG091N2\n",
                             ";;Gauge: 5\n",
                             ";;Width: 250\n",
                             ";;Carriers: 1 2 3 4 5 6 7 8 9 10\n",
                             ";;Position: Center\n"]

    def in_hook(self, yarn_carrier: Yarn_Carrier):
        """
        Declares that the in_hook for this yarn carrier is in use
        :param yarn_carrier: the yarn_carrier to bring in
        """
        self.in_hooks.add(yarn_carrier)
        self.yarns_in_operation.add(yarn_carrier)

    def release_hook(self, yarn_carrier: Yarn_Carrier):
        """
        Declares that the in-hook is not in use but yarn remains in use
        :param yarn_carrier: the yarn carrier to remove the inhook off
        """
        self.in_hooks.remove(yarn_carrier)

    def out_hook(self, yarn_carrier: Yarn_Carrier):
        """
        Declares that the yarn is no longer in service, will need to be in-hooked to use
        :param yarn_carrier: the yarn carrier to remove from service
        """
        assert yarn_carrier in self.yarns_in_operation, f"Cannot outhook {yarn_carrier} because its not in operation"
        if yarn_carrier in self.yarns_in_operation:
            self.yarns_in_operation.remove(yarn_carrier)
        for sub_carrier_id in yarn_carrier:
            sub_carrier = Yarn_Carrier(sub_carrier_id)
            if sub_carrier in self.yarns_in_operation:
                self.yarns_in_operation.remove(sub_carrier)

    def switch_carriage_direction(self):
        """
        Switches the last carriage direction set
        """
        self.last_carriage_direction = self.last_carriage_direction.opposite()

    @property
    def needle_count(self) -> int:
        """
        :return: the number of needles on either bed of the machine
        """
        return self.front_bed.needle_count

    def __len__(self):
        return self.needle_count

    def add_loop(self, loop_id: int, needle: Needle, carrier_set: Optional[Yarn_Carrier] = None, drop_prior_loops: bool = True):
        """
        Puts the loop_id on given needle, overrides existing loops as if a knit operation took place
        :param needle: The needle to add loops to
        :param carrier_set: the set  of yarns making this loop
        :param drop_prior_loops: If true, drops prior loops on the needle
        :param loop_id: the loop_id to be held on the needle
        """
        if carrier_set is not None:
            assert len(carrier_set.not_in_operation(self)) == 0, f"{carrier_set} not in operation"
        if needle.is_front:
            self.front_bed.add_loop(loop_id, needle, drop_prior_loops)
        else:
            self.back_bed.add_loop(loop_id, needle, drop_prior_loops)

    def drop_loop(self, needle: Needle):
        """
        Clears the loops held at this position as though a drop operation has been done.
        Also drops loop on sliders
        :param needle: The needle to drop loops from
        """
        if needle.is_front:
            self.front_bed.drop_loop(needle.position)
        else:
            self.back_bed.drop_loop(needle.position)

    def xfer_loops(self, start_needle: Needle, end_needle: Needle):
        """
        Xfer's the loop from the starting position to the ending position. Must transfer front to back or back to front
        :param start_needle:
        :param end_needle:
        """
        front_to_back = start_needle.is_front and end_needle.is_back
        if front_to_back:
            assert self.valid_rack(start_needle.position, end_needle.position), f"racking {self.racking} does not match f{start_needle.position} to b{end_needle.position}"
            assert start_needle.is_clear(self), f"{start_needle} is not clear for transfer"
            front_loops = self[start_needle]
            assert len(front_loops) > 0, f"No loop at {start_needle}"
            assert end_needle.is_clear(self), f"{end_needle} is not clear for transfer"
            for front_loop in front_loops:
                self.add_loop(front_loop, end_needle, drop_prior_loops=False)
        else:
            assert self.valid_rack(end_needle.position, start_needle.position), f"racking {self.racking} does not match b{start_needle.position} to f{end_needle.position}"
            assert start_needle.is_clear(self), f"{start_needle} is not clear for transfer"
            back_loops = self[start_needle]
            assert len(back_loops) > 0, f"No loop at {start_needle}"
            assert end_needle.is_clear(self), f"{end_needle} is not clear for transfer"
            for back_loop in back_loops:
                self.add_loop(back_loop, end_needle, drop_prior_loops=False)
        self.drop_loop(start_needle)

    def update_rack(self, front_pos: int, back_pos: int) -> Tuple[int, bool]:
        """
        Updates the current racking to align front and back
        :param front_pos: front needle to align
        :param back_pos: back needle to align
        :return: Return the updated racking, True if the racking is the same as original
        """
        original = self.racking
        self.racking = front_pos - back_pos
        return self.racking, original == self.racking

    def valid_rack(self, front_pos: int, back_pos: int) -> bool:
        """
        :param front_pos: the front needle in the racking
        :param back_pos: the back needle in the racking
        :return: True if the current racking can make this transfer
        """
        needed_rack = front_pos - back_pos
        return self.racking == needed_rack

    def __getitem__(self, item: Needle) -> List[int]:
        """
        :param item: the needle post, true if getting from the front
        :return: the loop held on the specified needle and bed
        """
        if item.is_front:
            return self.front_bed[item]
        else:
            return self.back_bed[item]

    def get_needle_of_loop(self, loop_id: int) -> Optional[Needle]:
        """
        :param loop_id: the loop being searched for
        :return: the needle holding the loop or None if it not held
        """
        front_needle = self.front_bed.get_needle_of_loop(loop_id)
        back_needle = self.back_bed.get_needle_of_loop(loop_id)
        if front_needle is None and back_needle is None:
            return None
        elif front_needle is None:
            return back_needle
        else:
            assert back_needle is None, f"Loop {loop_id} cannot be on f{front_needle.position} and b{back_needle.position}"
            return front_needle

    def add_carriage_pass(self, carriage_pass):
        """
        Executes the carriage pass on the current machine state
        :param carriage_pass: the carriage pass to execute
        """
        assert carriage_pass.machine_state == self, "Adding to different machine state"
        if len(carriage_pass.needles_to_instruction_parameters) > 0:
            self.carriage_passes.append(carriage_pass)
            self.instructions.extend(carriage_pass.write_instructions())

    def add_carriage_passes(self, add_passes: list):
        """
        Adds multiple carriage passes
        :param add_passes: list of passes to be added in order
        """
        for carriage_pass in add_passes:
            self.add_carriage_pass(carriage_pass)

    def write_instructions(self, filename: str):
        with open(filename, "w") as file:
            file.writelines(self.instructions)
