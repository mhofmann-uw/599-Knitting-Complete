from enum import Enum
from knitting_machine.Machine_State import Machine_State, Yarn_Carrier, Needle, Pass_Direction
from knitting_machine.machine_operations import outhook, miss, rack
from knitting_machine.operation_sets import Carriage_Pass, Instruction_Type, Instruction_Parameters

class Bend_Direction(Enum):
    Left = 1
    Right = 2
    Back = 3
    Front = 4

def _add_carriage_pass(carriage_pass, carriage_passes, instructions):
    if len(carriage_pass.needles_to_instruction_parameters) > 0:
        carriage_passes.append(carriage_pass)
        instructions.extend(carriage_pass.write_instructions())


def _write_instructions(filename: str, instructions):
    with open(filename, "w") as file:
        file.writelines(instructions)


def _cast_on(tuck_carrier, close_carrier, start_needle=0, end_needle=20, double=False):
    machine_state = Machine_State()
    carriage_passes = []
    instructions = [";!knitout-2\n",
                    ";;Machine: SWG091N2\n",
                    ";;Gauge: 5\n",
                    ";;Width: 250\n",
                    ";;Carriers: 1 2 3 4 5 6 7 8 9 10\n",
                    ";;Position: Center\n"]
    tuck_lr = {}
    for n in range(end_needle - 1, start_needle, -2):
        needle = Needle(True, n)
        tuck_lr[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, tuck_lr, machine_state), carriage_passes, instructions)
    tuck_rl = {}
    for n in range(start_needle, end_needle, 2):
        needle = Needle(True, n)
        tuck_rl[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, tuck_rl, machine_state), carriage_passes, instructions)

    if double:
        tuck_lr = {}
        for n in range(end_needle - 1, start_needle, -2):
            needle = Needle(False, n)
            tuck_lr[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, tuck_lr, machine_state), carriage_passes, instructions)
        tuck_rl = {}
        for n in range(start_needle, end_needle, 2):
            needle = Needle(False, n)
            tuck_rl[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, tuck_rl, machine_state), carriage_passes, instructions)

    knits = {}
    for n in range(end_needle - 1, start_needle - 1, -1):
        needle = Needle(True, n)
        knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=close_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)
    knits = {}
    for n in range(start_needle, end_needle):
        needle = Needle(not double, n)  # if double, knit a round by going on the back loops
        knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=close_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)
    return carriage_passes, instructions, machine_state


def _cast_on_round(tuck_carrier, close_carrier, start_needle=0, end_needle=20):
    machine_state = Machine_State()
    carriage_passes = []
    instructions = [";!knitout-2\n",
                    ";;Machine: SWG091N2\n",
                    ";;Gauge: 5\n",
                    ";;Width: 250\n",
                    ";;Carriers: 1 2 3 4 5 6 7 8 9 10\n",
                    ";;Position: Center\n"]
    # front RtL
    tuck_rl = {}
    for n in range(end_needle - 1, start_needle, -2):
        needle = Needle(True, n)
        tuck_rl[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, tuck_rl, machine_state), carriage_passes, instructions)
    # back LtR
    tuck_lr = {}
    for n in range(start_needle, end_needle, 2):
        needle = Needle(False, n)
        tuck_lr[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, tuck_lr, machine_state), carriage_passes, instructions)
    # front RtL others
    tuck_rl = {}
    for n in range(end_needle - 2, start_needle - 1, -2):
        needle = Needle(True, n)
        tuck_rl[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, tuck_rl, machine_state), carriage_passes, instructions)
    # back LtR others
    tuck_lr = {}
    for n in range(start_needle + 1, end_needle + 1, 2):
        needle = Needle(False, n)
        tuck_lr[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=tuck_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, tuck_lr, machine_state), carriage_passes, instructions)

    knits = {}
    # knit all in front RtL
    for n in range(end_needle - 1, start_needle - 1, -1):
        needle = Needle(True, n)
        knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=close_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)
    knits = {}
    # knit all in back LtR
    for n in range(start_needle, end_needle):
        needle = Needle(False, n)
        knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=close_carrier)
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)
    return carriage_passes, instructions, machine_state


def test_tube(width: int = 20, height: int = 20, carrier:int=3):
    c1 = Yarn_Carrier(carrier)
    circ = width * 2
    """
    width = circ//2
    if circ % 2 == 1:
        width = circ//2+1
    """
    carriage_passes, instructions, machine_state = _cast_on_round(c1, c1, start_needle=0, end_needle=width)
    instructions.append(rack(machine_state, -.75))  # rack for all needle knitting
    for row in range(0, height):
        knits = {}
        # front RtL
        for n in range(width-1, -1, -1):
            front_needle = Needle(True, n)
            knits[front_needle] = Instruction_Parameters(front_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)

        knits = {}
        # back LtR
        for n in range(0, width):
            back_needle = Needle(False, n)
            knits[back_needle] = Instruction_Parameters(back_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)

    instructions.append(outhook(machine_state, c1))

    _write_instructions("tube.k", instructions)


def tube_helper(width, height, c1, machine_state, carriage_passes, instructions):
    for row in range(0, height):
        knits = {}
        # front RtL
        for n in range(width-1, -1, -1):
            front_needle = Needle(True, n)
            knits[front_needle] = Instruction_Parameters(front_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)

        knits = {}
        # back LtR
        for n in range(0, width):
            back_needle = Needle(False, n)
            knits[back_needle] = Instruction_Parameters(back_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)


"""
adds short rows to the front using this shape
XXXXXXX
 XXXXX
  XXX
   X
  XXX
 XXXXX
XXXXXXX
"""
def iso_bend_helper(width, height, bend_dir, c1, machine_state, carriage_passes, instructions):
    # shrink
    is_front = bend_dir is Bend_Direction.Front
    if is_front:
        pass_dir = Pass_Direction.Right_to_Left
    else:
        pass_dir = Pass_Direction.Left_to_Right
        knits = {}
        for n in range(width-1, -1, -1):
            front_needle = Needle(True, n)
            knits[front_needle] = Instruction_Parameters(front_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)

    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # front RtL
            for n in range(width-1-row, -1+row, -1):
                print(n)
                needle = Needle(is_front, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state), carriage_passes, instructions)
        else:
            # front LtR
            for n in range(row, width-row):
                print(n)
                needle = Needle(is_front, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state), carriage_passes, instructions)
        print("newline")
    # grow
    # ensure we are starting off in the right direction
    if height % 2 == 0:
        even_dir = pass_dir
        odd_dir = pass_dir.opposite()
    else:
        even_dir = pass_dir.opposite()
        odd_dir = pass_dir

    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # front even_dir
            for n in range(width-height+row, -1+height-row-1, -1):
                print(n)
                needle = Needle(is_front, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, even_dir, knits, machine_state), carriage_passes, instructions)
        else:
            # front odd_dir
            for n in range(height-row-1, width-height+row+1):
                print(n)
                needle = Needle(is_front, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, odd_dir, knits, machine_state), carriage_passes, instructions)
        print("newline")
    if not is_front:
        knits = {}
        for n in range(0, width):
            back_needle = Needle(False, n)
            knits[back_needle] = Instruction_Parameters(back_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)

"""
adds short rows to the front using this shape
XXXX
 XXX
  XX
   X
  XX
 XXX
XXXX
"""
def right_bend_helper(width, height, c1, machine_state, carriage_passes, instructions):
    # shrink
    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # front RtL
            for n in range(width-1, -1+row, -1):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)
        else:
            # front LtR
            for n in range(row, width):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)
    # grow
    # ensure we are starting off in the right direction
    if height % 2 == 0:
        even_dir = Pass_Direction.Right_to_Left
        odd_dir = Pass_Direction.Left_to_Right
    else:
        even_dir = Pass_Direction.Left_to_Right
        odd_dir = Pass_Direction.Right_to_Left

    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # front even_dir
            for n in range(width-1, -2+height-row, -1): #off by one?
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, even_dir, knits, machine_state), carriage_passes, instructions)
        else:
            # front odd_dir
            for n in range(height-row-1, width):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, odd_dir, knits, machine_state), carriage_passes, instructions)


"""
adds short rows to the front using this shape
XXXX
XXX
XX
X
XX
XXX
XXXX
"""
def left_bend_helper(width, height, c1, machine_state, carriage_passes, instructions):
    # shrink
    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # front RtL
            for n in range(width-1-row, -1, -1):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)
        else:
            # front LtR
            for n in range(0, width-row):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)
    # grow
    # ensure we are starting off in the right direction
    if height % 2 == 0:
        even_dir = Pass_Direction.Right_to_Left
        odd_dir = Pass_Direction.Left_to_Right
    else:
        even_dir = Pass_Direction.Left_to_Right
        odd_dir = Pass_Direction.Right_to_Left

    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # front even_dir
            for n in range(width-height+row, -1, -1):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, even_dir, knits, machine_state), carriage_passes, instructions)
        else:
            # front odd_dir
            for n in range(0, width-height+row+1):
                needle = Needle(True, n)
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, odd_dir, knits, machine_state), carriage_passes, instructions)


def test_tube_bent(width, height, bend_loc, bend_height, bend_dir, carrier:int=3):
    assert bend_loc < height

    if bend_dir is Bend_Direction.Back or Bend_Direction.Front:
        assert bend_height <= width/2
    elif bend_dir is Bend_Direction.Left or Bend_Direction.Right:
        assert bend_height < width
    else:
        print("error")

    c1 = Yarn_Carrier(carrier)
    circ = width * 2
    """
    width = circ//2
    if circ % 2 == 1:
        width = circ//2+1
    """
    carriage_passes, instructions, machine_state = _cast_on_round(c1, c1, start_needle=0, end_needle=width)
    instructions.append(rack(machine_state, -.75))  # rack for all needle knitting
    # Straight part
    tube_helper(width, bend_loc, c1, machine_state, carriage_passes, instructions)
    # Bent part
    #side_bend_helper(width, bend_height, c1, machine_state, carriage_passes, instructions)
    if bend_dir is Bend_Direction.Left:
        left_bend_helper(width, bend_height, c1, machine_state, carriage_passes, instructions)
        #center_bend_helper(width, bend_height, c1, machine_state, carriage_passes, instructions)
    elif bend_dir is Bend_Direction.Right:
        right_bend_helper(width, bend_height, c1, machine_state, carriage_passes, instructions)
    elif bend_dir is Bend_Direction.Back or Bend_Direction.Front:
        iso_bend_helper(width, bend_height, bend_dir, c1, machine_state, carriage_passes, instructions)
    else:
        print("error")

    # Straight part
    tube_helper(width, height-bend_loc, c1, machine_state, carriage_passes, instructions)

    instructions.append(outhook(machine_state, c1))

    _write_instructions("tube_bent.k", instructions)


if __name__ == "__main__":
    #test_tube(20, 40, 3)
    #test_tube_bent(10, 40, 20, 3, True, 3)

    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Left, 3)
    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Right, 3)
    test_tube_bent(10, 20, 10, 4, Bend_Direction.Front, 3)
    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Back, 3)

