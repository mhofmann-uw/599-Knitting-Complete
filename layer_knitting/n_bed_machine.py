import math
from typing import List, Optional, Dict, Tuple

from knitting_machine.Machine_State import Machine_State, Pass_Direction
from knitting_machine.needles import Needle, Slider_Needle
from knitting_machine.operation_sets import Carriage_Pass, Instruction_Parameters, Instruction_Type
from knitting_machine.yarn_carrier import Yarn_Carrier


class N_Bed_Machine_State(Machine_State):
    """
    A representation of a multi-bed machine using gauging
    """

    def __init__(self, layers=3, needle_count: int = 250, racking: float = 0):
        super().__init__(needle_count, racking)
        self.layers = layers
        self.layers_to_front_Needles: Dict[int, List[Needle]] = {lyr: [] for lyr in range(0, self.layers)}
        self.layers_to_front_Sliders: Dict[int, List[Slider_Needle]] = {lyr: [] for lyr in range(0, self.layers)}
        self.layers_to_back_Needles: Dict[int, List[Needle]] = {lyr: [] for lyr in range(0, self.layers)}
        self.layers_to_back_Sliders: Dict[int, List[Slider_Needle]] = {lyr: [] for lyr in range(0, self.layers)}

    def set_to_layer(self, layer: int):
        """
        Positions all other layers according to next layer to be knit and resets for that layer from past transfers
        :param layer: the layer to be knit next
        """
        # bring prior layers to front
        for prior_layer in range(0, layer):
            self.bring_layer_to_front(prior_layer)
        # bring after layers to back
        for next_layer in range(layer + 1, self.layers):
            self.bring_layer_to_back(next_layer)
        # put front needles on front
        fronts = {}
        for front_needle in self.layers_to_front_Needles[layer]:
            holding_needle = front_needle.opposite(slider=True)
            fronts[holding_needle] = Instruction_Parameters(holding_needle, needle_2=front_needle)
        self.add_carriage_pass(Carriage_Pass(Instruction_Type.Xfer, direction=None, needles_to_instruction_parameters=fronts,
                                             machine_state=self, pass_comment=f"reset front layer {layer}"))
        # put front sliders on sliders
        front_sliders = {}
        for front_slider in self.layers_to_front_Sliders[layer]:
            holding_needle = front_slider.opposite(slider=True)
            front_sliders[holding_needle] = Instruction_Parameters(holding_needle, needle_2=front_slider)
        self.add_carriage_pass(Carriage_Pass(Instruction_Type.Xfer, direction=None, needles_to_instruction_parameters=front_sliders,
                                             machine_state=self, pass_comment=f"reset front sliders layer {layer}"))
        # put back needles on back
        backs = {}
        for back_needle in self.layers_to_back_Needles[layer]:
            holding_needle = back_needle.opposite(slider=True)
            backs[holding_needle] = Instruction_Parameters(holding_needle, needle_2=back_needle)
        self.add_carriage_pass(Carriage_Pass(Instruction_Type.Xfer, direction=None, needles_to_instruction_parameters=backs,
                                             machine_state=self, pass_comment=f"reset back layer {layer}"))
        # put front sliders on sliders
        back_sliders = {}
        for back_slider in self.layers_to_back_Sliders[layer]:
            holding_needle = back_slider.opposite(slider=True)
            back_sliders[holding_needle] = Instruction_Parameters(holding_needle, needle_2=back_slider)
        self.add_carriage_pass(Carriage_Pass(Instruction_Type.Xfer, direction=None, needles_to_instruction_parameters=back_sliders,
                                             machine_state=self, pass_comment=f"reset back sliders layer {layer}"))


    @property
    def layer_needle_count(self) -> int:
        """
        :return: the number of needles usable on a given layer
        """
        return math.floor(self.needle_count / self.layers)

    def add_loop_to_layer(self, layer: int, loop_id: int, needle: Needle, carrier_set: Optional[Yarn_Carrier] = None, drop_prior_loops: bool = True):
        """
        Puts the loop_id on given needle (considering layering gauging. Overrides existing loops if knitting
        :param layer: the layer of the needle being worked with
        :param loop_id: the loop_id to be held on the needle
        :param needle: THe needle (not gauged) to add to
        :param carrier_set: the set  of yarns making this loop
        :param drop_prior_loops: If true, drops prior loops on the needle
        """
        actual_needle = self.get_actual_needle(needle, layer)
        self.add_loop(loop_id, actual_needle, carrier_set, drop_prior_loops)

    def get_actual_needle(self, needle: Needle, layer: int) -> Needle:
        """
        :param needle: the needle indexed to an N-bed
        :param layer: the layer held on this needle (0 is front)
        :return: The needle on the standard V-bed + Sliders corresponding to the n-bed needle
        """
        assert layer < self.layers
        actual_pos = (needle.position * self.layers) + layer
        if needle.is_slider:
            return Slider_Needle(needle.is_front, actual_pos)
        else:
            return Needle(needle.is_front, actual_pos)

    def needles_of_layer(self, layer: int, include_front: bool = False, include_front_sliders: bool = False,
                         include_back: bool = False, include_back_sliders: bool = False) -> List[Needle]:
        """
        :param layer: The layer (0-front) to gauge from
        :param include_front: if true, give front needles
        :param include_front_sliders:  if true, give front sliders
        :param include_back:  if true, give back needles
        :param include_back_sliders:  if true, give back sliders
        :return: A list of needles (0 -> N) at the given gauge for the given layer
        """
        assert layer < self.layers
        needles = []
        for needle_pos in range(layer, self.needle_count, self.layers):
            if include_front:
                needles.append(Needle(True, needle_pos))
            if include_front_sliders:
                needles.append(Slider_Needle(True, needle_pos))
            if include_back:
                needles.append(Needle(False, needle_pos))
            if include_back_sliders:
                needles.append(Slider_Needle(False, needle_pos))
        return needles

    def _xfer_layer(self, starting_needles, starting_sliders) -> Tuple[List[Needle], List[Slider_Needle]]:
        slider_xfers = {}
        return_sliders = []
        for slider in starting_sliders:
            loops = self[slider]
            if len(loops) > 0:  # loops on the slider to xfer
                target = slider.opposite(slider=True)
                slider_xfers[slider] = Instruction_Parameters(slider, needle_2=target)
                return_sliders.append(slider)
        self.add_carriage_pass(Carriage_Pass(Instruction_Type.Xfer, direction=None, needles_to_instruction_parameters=slider_xfers,
                                             machine_state=self, pass_comment="xfer_sliders of layer"))
        xfers = {}
        return_needles = []
        for needle in starting_needles:
            loops = self[needle]
            if len(loops) > 0:  # loops on the needle to xfer
                target = needle.opposite(slider=True)
                xfers[needle] = Instruction_Parameters(needle, needle_2=target)
                return_needles.append(needle)
        self.add_carriage_pass(Carriage_Pass(Instruction_Type.Xfer, direction=None, needles_to_instruction_parameters=xfers,
                                             machine_state=self, pass_comment="xfer_needles of layer"))
        return return_needles, return_sliders

    def bring_layer_to_front(self, layer: int):
        """
        Transfers the back-bed loops to sliders on front-bed (puts layer in front of next operations
        :param layer: The layer to be brought to front
        """
        assert layer < self.layers
        back_needles = self.needles_of_layer(layer, include_back=True)
        back_sliders = self.needles_of_layer(layer, include_back_sliders=True)
        return_needles, return_sliders = self._xfer_layer(back_needles, back_sliders)
        self.layers_to_back_Needles[layer] = return_needles
        self.layers_to_back_Sliders[layer] = return_sliders

    def bring_layer_to_back(self, layer: int):
        """
        Transfers front-bed loops to sliders on back bed (puts layer behind next operations
        :param layer: The layer to be brought to front
        """
        assert layer < self.layers
        front_needles = self.needles_of_layer(layer, include_front=True)
        front_sliders = self.needles_of_layer(layer, include_front_sliders=True)
        return_needles, return_sliders = self._xfer_layer(front_needles, front_sliders)
        self.layers_to_front_Needles[layer] = return_needles
        self.layers_to_front_Sliders[layer] = return_sliders

    def front_needle_sheet_cast_on(self, width: int, layer_to_yarn_carrier: Dict[int, Yarn_Carrier],
                                   layer_to_direction: Dict[int, Pass_Direction]):
        """
        Creates carriage passes for an alternating tuck cast on of each layer
        :param width: the number of loops per layer
        :param layer_to_yarn_carrier: the yarn-carrier used for each layer
        :param layer_to_direction: the direction each layer will move
        :return: list of carriage passes to execute cast on
        """

        def _do_right_left_tucks(do_drop: bool):
            right_left_tucks = {}
            for n in range(width - 1, 0, -2):
                layer_needle = Needle(True, n)
                actual_needle = self.get_actual_needle(layer_needle, layer)
                right_left_tucks[actual_needle] = Instruction_Parameters(actual_needle, involved_loop=-1, carrier=carrier)
            if do_drop:  # odd cast on, tuck after actual loops
                drop_needle = Needle(True, width)
                right_left_tucks[drop_needle] = Instruction_Parameters(drop_needle, involved_loop=-1, carrier=carrier)
                drops[drop_needle] = Instruction_Parameters(drop_needle)
            return Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, right_left_tucks, self, pass_comment="right-to-left cast on")

        def _do_left_right_tucks(do_drop: bool):
            left_right_tucks = {}
            if do_drop:  # odd cast on, tuck before actual loops
                drop_needle = Needle(True, -1)
                left_right_tucks[drop_needle] = Instruction_Parameters(drop_needle, involved_loop=-1, carrier=carrier)
                drops[drop_needle] = Instruction_Parameters(drop_needle)
            for n in range(0, width, 2):
                layer_needle = Needle(True, n)
                actual_needle = self.get_actual_needle(layer_needle, layer)
                left_right_tucks[actual_needle] = Instruction_Parameters(actual_needle, involved_loop=-1, carrier=carrier)
            return Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, left_right_tucks, self, pass_comment="left-to-right cast on")

        for layer in range(0, self.layers):
            self.set_to_layer(layer)
            carrier = layer_to_yarn_carrier[layer]
            direction = layer_to_direction[layer]
            drops = {}
            if direction is Pass_Direction.Right_to_Left:  # ends back on right side
                right_left_pass = _do_right_left_tucks(False)
                self.add_carriage_pass(right_left_pass)
                left_right_pass = _do_left_right_tucks(width % 2 == 1)
                self.add_carriage_pass(left_right_pass)
            else:
                left_right_pass = _do_left_right_tucks(False)
                self.add_carriage_pass(left_right_pass)
                right_left_pass = _do_right_left_tucks(width % 2 == 1)
                self.add_carriage_pass(right_left_pass)
            if len(drops) > 0:  # drop first tuck
                self.add_carriage_pass(Carriage_Pass(Instruction_Type.Drop, direction=Pass_Direction.Left_to_Right,
                                                     needles_to_instruction_parameters=drops, machine_state=self,
                                                     pass_comment="drop stabilizing tuck"))

    def all_needle_sheet_cast_on(self, width: int, layer_to_yarn_carrier: Dict[int, Yarn_Carrier],
                                 layer_to_direction: Dict[int, Pass_Direction]):
        """
        Does an alternating all-needle cast on for each layer
        :param width: the number of loops across each layer
        :param layer_to_yarn_carrier: the yarn-carrier used for each layer
        :param layer_to_direction: the knit-graph direction for each layer
        :return:
        """

        def _front_mod(n, m):
            if n % 2 == m:
                front = True
            else:
                front = False
            return front

        def _do_right_left():
            right_left_tucks = {}
            for n in range(width - 1, -1, -1):
                layer_needle = Needle(_front_mod(n, mod), n)
                actual_needle = self.get_actual_needle(layer_needle, layer)
                right_left_tucks[actual_needle] = Instruction_Parameters(actual_needle, involved_loop=-1,
                                                                         carrier=carrier)
            return Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, right_left_tucks, self,
                                 pass_comment="right-to-left cast on")

        def _do_left_right():
            left_right_tucks = {}
            for n in range(0, width, 1):
                layer_needle = Needle(not _front_mod(n, mod), n)
                actual_needle = self.get_actual_needle(layer_needle, layer)
                left_right_tucks[actual_needle] = Instruction_Parameters(actual_needle, involved_loop=-1,
                                                                         carrier=carrier)
            return Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, left_right_tucks, self,
                                 pass_comment="left-to-right-cast on")

        for layer in range(0, self.layers):
            self.set_to_layer(layer)
            carrier = layer_to_yarn_carrier[layer]
            direction = layer_to_direction[layer]
            mod = (width - 1) % 2
            if direction is Pass_Direction.Right_to_Left:  # end back on right
                right_left_pass = _do_right_left()
                self.add_carriage_pass(right_left_pass)
                left_right_pass = _do_left_right()
                self.add_carriage_pass(left_right_pass)
            else:
                left_right_pass = _do_left_right()
                self.add_carriage_pass(left_right_pass)
                right_left_pass = _do_right_left()
                self.add_carriage_pass(right_left_pass)
