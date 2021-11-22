from knitting_machine.Machine_State import Pass_Direction
from knitting_machine.machine_operations import outhook
from knitting_machine.needles import Needle
from knitting_machine.operation_sets import Instruction_Parameters, Carriage_Pass, Instruction_Type
from knitting_machine.yarn_carrier import Yarn_Carrier
from layer_knitting.n_bed_machine import N_Bed_Machine_State


def _write_instructions(filename: str, instructions):
    with open(filename, "w") as file:
        file.writelines(instructions)


def test_round_jacquard():
    c1 = Yarn_Carrier(3)
    c2 = Yarn_Carrier(4)
    n_bed_state = N_Bed_Machine_State(layers=2)
    width = 20
    height = 20
    n_bed_state.all_needle_sheet_cast_on(width, {0: c1, 1: c2}, {0: Pass_Direction.Right_to_Left, 1: Pass_Direction.Right_to_Left})

    for row in range(0, height):
        # front layer (double jacquard alternating colors)
        n_bed_state.set_to_layer(0)
        c1_knits = {}
        c2_knits = {}
        for n in range(width - 1, -1, -1):  # Right to left Pass
            # knit alternating wales of color from right to left
            front_needle = Needle(True, n)
            actual_front = n_bed_state.get_actual_needle(front_needle, 0)
            actual_back = actual_front.opposite()
            if n % 2 == 0:
                c1_needle = actual_front
                c2_needle = actual_back
            else:
                c1_needle = actual_back
                c2_needle = actual_front
            c1_knits[c1_needle] = Instruction_Parameters(c1_needle, -1, carrier=c1)
            c2_knits[c2_needle] = Instruction_Parameters(c2_needle, -1, carrier=c2)
        n_bed_state.add_carriage_pass(Carriage_Pass(Instruction_Type.Knit,
                                                    Pass_Direction.Right_to_Left,
                                                    c1_knits, n_bed_state, pass_comment=f"{row}: {c1} front"))
        n_bed_state.add_carriage_pass(Carriage_Pass(Instruction_Type.Knit,
                                                    Pass_Direction.Right_to_Left,
                                                    c2_knits, n_bed_state, pass_comment=f"{row}: {c2} front"))
        # back layer (double jacquard checkered colors)
        n_bed_state.set_to_layer(1)
        c1_knits = {}
        c2_knits = {}
        for n in range(0, width):  # left to right pass
            # knit a checkered pattern from left to right
            front_needle = Needle(True, n)
            actual_front = n_bed_state.get_actual_needle(front_needle, 1)
            actual_back = actual_front.opposite()
            if n % 2 == row % 2:  # does checker-pattern
                c1_needle = actual_front
                c2_needle = actual_back
            else:
                c1_needle = actual_back
                c2_needle = actual_front
            c1_knits[c1_needle] = Instruction_Parameters(c1_needle, -1, carrier=c1)
            c2_knits[c2_needle] = Instruction_Parameters(c2_needle, -1, carrier=c2)
        n_bed_state.add_carriage_pass(Carriage_Pass(Instruction_Type.Knit,
                                                    Pass_Direction.Left_to_Right,
                                                    c1_knits, n_bed_state, pass_comment=f"{row}: {c1} back"))
        n_bed_state.add_carriage_pass(Carriage_Pass(Instruction_Type.Knit,
                                                    Pass_Direction.Left_to_Right,
                                                    c2_knits, n_bed_state, pass_comment=f"{row}: {c2} back"))

    n_bed_state.instructions.append(outhook(n_bed_state, c1))
    n_bed_state.instructions.append(outhook(n_bed_state, c2))

    n_bed_state.write_instructions("round_jacquard.k")
