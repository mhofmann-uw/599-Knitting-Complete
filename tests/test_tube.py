from enum import Enum
from knitting_machine.Machine_State import Machine_State, Yarn_Carrier, Needle, Pass_Direction
from knitting_machine.machine_operations import outhook
from knitting_machine.operation_sets import Carriage_Pass, Instruction_Type, Instruction_Parameters

class Bend_Direction(Enum):
    Left = "left"
    Right = "right"
    Back = "back"
    Front = "front"

class Bend:
    """
    A Simple class structure for representing a bend
    """

    def __init__(self, position: int, height: int, bend_dir: Bend_Direction):
        """
        :param position: where along the length of the snake the bend takes place
        :param height: how tall the bend is
        :param bend_dir: which way the bend goes
        """
        #self.width: int = width
        self.position: int = position
        self.height: int = height
        self.bend_dir: Bend_Direction = bend_dir
        #assert self.width is not None
        assert self.position is not None
        assert self.height is not None
        assert self.bend_dir is not None
    """
        if bend_dir is Bend_Direction.Back or bend_dir is Bend_Direction.Front:
            assert height <= width / 2
        elif bend_dir is Bend_Direction.Left or bend_dir is Bend_Direction.Right:
            assert height < width
        else:
            raise AttributeError

    """

    def __str__(self):
        return f"bend {self.position}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.position

    def __lt__(self, other):
        if isinstance(other, Bend):
            return self.position < other.position
        elif type(other) is int:
            return self.position < other
        else:
            raise AttributeError


def _add_carriage_pass(carriage_pass, carriage_passes, instructions):
    if len(carriage_pass.needles_to_instruction_parameters) > 0:
        carriage_passes.append(carriage_pass)
        instructions.extend(carriage_pass.write_instructions())


def _write_instructions(filename: str, instructions):
    with open(filename, "w") as file:
        file.writelines(instructions)


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


def should_switch_directions(n, width, cur_dir):
    return (cur_dir is Pass_Direction.Right_to_Left and (n % (width*2) == width-1 or n % (width*2) == width)) or (cur_dir is Pass_Direction.Left_to_Right and (n % (width*2) == width*2-1 or n % (width*2) == 0))

"""
adds short rows to the bend_dir using this shape
XXXXXXX
 XXXXX
  XXX
   X
  XXX
 XXXXX
XXXXXXX
"""
def iso_bend_shifted_helper(width, height, c1, machine_state, carriage_passes, instructions, bend_shift=0):
    """
    :param: width is same as body width and short row triangle width
    :param: bend_shift is an int >= 0 and < width*2 that is where the bend triangle starts.
    """
    # map ints to needles
    #print("width", width)
    needles = []
    for f in range(width-1, -1, -1):
        needles.append(Needle(True, f))
    for b in range(0, width):
        needles.append(Needle(False, b))
    indices = dict(list(enumerate(needles)))
    print(indices)

    print("pres start")
    #instructions.append("starting pres")

    # add regular knits up to the place the bend is shifted to
    knits = {}
    pass_dir = Pass_Direction.Right_to_Left
    for n in range(0, bend_shift):
        print(n)
        if n < width:
            pass_dir = Pass_Direction.Right_to_Left
        else:
            pass_dir = Pass_Direction.Left_to_Right
        needle = needles[n]
        knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1, comment="course num")
        # if at about to change dirs, do a carriage pass
        if n < bend_shift-1 and should_switch_directions(n, width, pass_dir):
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                               carriage_passes, instructions)
            knits = {}
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state), carriage_passes, instructions)
    print("pres end")
    #instructions.append("done w pres")

    instructions.append("starting short rows")

    # shrink
    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # RtL
            for n in range(bend_shift + row, bend_shift + width - row):  # might be wrong
                print(n)
                if n % (width * 2) < width:
                    pass_dir = Pass_Direction.Right_to_Left
                else:
                    pass_dir = Pass_Direction.Left_to_Right
                needle = needles[n % (width * 2)]
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1, comment="course num")
                print(needle, pass_dir)
                # if at about to change dirs, do a carriage pass
                if n < bend_shift + width - row-1 and should_switch_directions(n, width, pass_dir):
                    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                                       carriage_passes, instructions)
                    knits = {}
                    print("change dir")
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                               carriage_passes, instructions)

        else:
            # LtR
            for n in range(bend_shift+width-row-1, bend_shift-1+row, -1): # might be wrong
                print(n)
                if n % (width*2) < width:
                    pass_dir = Pass_Direction.Right_to_Left
                else:
                    pass_dir = Pass_Direction.Left_to_Right
                needle = needles[n % (width*2)]
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1, comment="course num")
                print(needle, pass_dir.opposite())
                # if at about to change dirs, do a carriage pass
                if n > bend_shift-1+row+1 and should_switch_directions(n, width, pass_dir.opposite()):
                    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                       carriage_passes, instructions)
                    knits = {}
                    print("change dir")
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state), carriage_passes, instructions)
        print("newline")
    instructions.append("middle")
    print("middle")
    # grow
    # ensure we are starting off in the right direction
    """
        if height % 2 == 1:
            starting_dir = pass_dir
            #odd_dir = pass_dir.opposite()
        else:
            starting_dir = pass_dir.opposite()
            #odd_dir = pass_dir
    
    n = bend_shift+width+row-height
    if n % (width * 2) < width:
        starting_dir = pass_dir.opposite()

    else:
        starting_dir = pass_dir
    """
    dr = bend_shift+width+row-height

    #if dr % (width * 2) < width:
    if height % 2 == 0:
        #starting_dir = Pass_Direction.Right_to_Left
        #pass_dir = starting_dir
        for row in range(0, height):
            knits = {}
            if row % 2 == 0:
                # clockwise
                for n in range(bend_shift + width + row - height, bend_shift - 1 - row + height - 1,
                               -1):  # might be wrong
                    print(n)
                    if n % (width * 2) < width:
                        #pass_dir = starting_dir
                        pass_dir = Pass_Direction.Right_to_Left
                    else:
                        #pass_dir = starting_dir.opposite
                        pass_dir = Pass_Direction.Left_to_Right
                    needle = needles[n % (width * 2)]
                    knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                    print(needle, pass_dir)
                    # if at about to change dirs, do a carriage pass
                    if n > bend_shift - 1 - row + height - 1 + 1 and should_switch_directions(n, width, pass_dir):
                        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                                           carriage_passes, instructions)
                        instructions.append("dir change")
                        knits = {}
                        print("change dir")
                _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                                   carriage_passes, instructions)
                instructions.append("this is an even row for an even height")
            else:
                # counter clockwise
                for n in range(bend_shift - row + height - 1, bend_shift + width + row + 1 - height):  # might be wrong
                    print(n)
                    if n % (width * 2) < width:
                        #pass_dir = starting_dir.opposite()
                        pass_dir = Pass_Direction.Right_to_Left
                    else:
                        #pass_dir = starting_dir
                        pass_dir = Pass_Direction.Left_to_Right
                    needle = needles[n % (width * 2)]
                    knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                    print(needle, pass_dir.opposite())
                    # if at about to change dirs, do a carriage pass
                    if n < bend_shift + width + row + 1 - height - 1 and should_switch_directions(n, width,
                                                                                                  pass_dir.opposite()):
                        _add_carriage_pass(
                            Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                            carriage_passes, instructions)
                        instructions.append("dir change")
                        knits = {}
                        print("change dir")
                _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                   carriage_passes, instructions)
                instructions.append("this is an odd row for an even height")
            print("newline")

    else:
        #starting_dir = Pass_Direction.Left_to_Right
        #pass_dir = starting_dir
        for row in range(0, height):
            knits = {}
            if row % 2 == 0:
                # counter clockwise
                for n in range(bend_shift + width + row - height, bend_shift - 1 - row + height - 1,
                               -1):  # might be wrong
                    print(n)
                    if n % (width * 2) < width:
                        #pass_dir = starting_dir
                        pass_dir = Pass_Direction.Left_to_Right
                    else:
                        #pass_dir = starting_dir.opposite()
                        pass_dir = Pass_Direction.Right_to_Left
                    needle = needles[n % (width * 2)]
                    knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                    print(needle, pass_dir)
                    # if at about to change dirs, do a carriage pass
                    if n > bend_shift - 1 - row + height - 1 + 1 and should_switch_directions(n, width, pass_dir):
                        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                                           carriage_passes, instructions)
                        instructions.append("dir change")
                        knits = {}
                        print("change dir")
                _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                                   carriage_passes, instructions)
                instructions.append("this is an even row for an odd height")

            else:
                # clockwise
                for n in range(bend_shift - row + height - 1, bend_shift + width + row + 1 - height):  # might be wrong
                    print(n)
                    if n % (width * 2) < width:
                        #pass_dir = starting_dir.opposite()
                        pass_dir = Pass_Direction.Left_to_Right
                    else:
                        #pass_dir = starting_dir
                        pass_dir = Pass_Direction.Right_to_Left
                    needle = needles[n % (width * 2)]
                    knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                    print(needle, pass_dir.opposite())
                    # if at about to change dirs, do a carriage pass
                    if n < bend_shift + width + row + 1 - height - 1 and should_switch_directions(n, width,
                                                                                                  pass_dir.opposite()):
                        _add_carriage_pass(
                            Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                            carriage_passes, instructions)
                        instructions.append("dir change")
                        knits = {}
                        print("change dir")
                _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                   carriage_passes, instructions)
                instructions.append("this is an odd row for an odd height")
            print("newline")


    instructions.append("done with short rows")
    # add extras to complete the round
    if bend_shift > 0:
        #instructions.append("starting posts")
        knits = {}
        for n in range(bend_shift+1, width*2):
            if n < width:
                pass_dir = Pass_Direction.Right_to_Left
            else:
                pass_dir = Pass_Direction.Left_to_Right
            needle = needles[n]
            knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
            # if at about to change dirs, do a carriage pass
            if n < width*2-1 and should_switch_directions(n, width, pass_dir.opposite()):
                _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                   carriage_passes, instructions)
                knits = {}
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state), carriage_passes, instructions)
        #instructions.append("done w posts")


def test_multi_bend(width, end, bends, file, carrier:int=3):
    if len(file) < 1:
        file = "snek"
    if bends:
        for i in range(0, len(bends)):
            cur = bends[i]
            if i > 0:
                # ensure bends array is in increasing order
                assert cur.position >= bends[i-1].position

            if cur.bend_dir is Bend_Direction.Back or cur.bend_dir is Bend_Direction.Front:
                assert cur.height <= width/2
            elif cur.bend_dir is Bend_Direction.Left or cur.bend_dir is Bend_Direction.Right:
                assert cur.height < width
            else:
                assert cur.height <= width/2

    c1 = Yarn_Carrier(carrier)
    circ = width * 2
    """
    width = circ//2
    if circ % 2 == 1:
        width = circ//2+1
    """
    #height = bends[len(bends)-1].position + end + 1
    carriage_passes, instructions, machine_state = _cast_on_round(c1, c1, start_needle=0, end_needle=width)
    #instructions.append(rack(machine_state, -.75))  # rack for all needle knitting

    cur = 0
    if bends:
        for i in range(0, len(bends)):
            cur_bend = bends[i]
            pos = cur_bend.position
            bend_dir = cur_bend.bend_dir
            print("cur", cur)
            print("pos", pos)
            print("bend dir", bend_dir)
            if cur > pos:
                raise RuntimeError
            elif cur < pos:
                # Straight part
                tube_helper(width, pos-cur, c1, machine_state, carriage_passes, instructions)
                cur = pos
            # Bent part
            # bend starts in a particular location
            print("shifted")
            iso_bend_shifted_helper(width, cur_bend.height, c1, machine_state, carriage_passes, instructions, bend_dir)

    # Straight part
    if end > 0:
        tube_helper(width, end, c1, machine_state, carriage_passes, instructions)

    instructions.append(outhook(machine_state, c1))
    _write_instructions(file+".k", instructions)


if __name__ == "__main__":
    #to knit
    #test_multi_bend(16, 5, [Bend(2, 8, 0), Bend(4, 8, 6), Bend(6, 8, 0), Bend(8, 8, 6), Bend(10, 8, 0), Bend(12, 8, 6)], "largercentered6bends", 3)
    #test_multi_bend(16, 5, [Bend(2, 8, 0), Bend(4, 8, 0), Bend(6, 8, 0), Bend(8, 8, 0), Bend(10, 8, 0), Bend(12, 8, 0), Bend(14, 8, 0), Bend(16, 8, 0), Bend(18, 8, 0)], "bendonself", 3)
    #test_multi_bend(16, 5, [Bend(5, 1, 0), Bend(10, 2, 0), Bend(15, 3, 0), Bend(20, 4, 0), Bend(25, 5, 0), Bend(30, 6, 0), Bend(35, 7, 0), Bend(40, 8, 0)], "diffheightscommented", 3)
    #test_multi_bend(16, 2, [Bend(2, 1, 0), Bend(4, 2, 0)], "smalldiffheightscommented", 3)

    test_multi_bend(10, 2, [Bend(2, 2, 0), Bend(4, 4, 0)], "smalldiffheightsevens", 3)
    test_multi_bend(10, 2, [Bend(2, 1, 0), Bend(4, 3, 0), Bend(6, 5, 0)], "smalldiffheightsodds", 3)




