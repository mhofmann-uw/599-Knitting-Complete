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
        knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
        # if at about to change dirs, do a carriage pass
        if should_switch_directions(n, width, pass_dir):
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                               carriage_passes, instructions)
            knits = {}
    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state), carriage_passes, instructions)
    print("pres end")
    #instructions.append("done w pres")

    #instructions.append("starting short rows")
    """
    if bend_shift <= width:
        knits = {}
        for n in range(width-1, bend_shift, -1):  # add extras to front up to bend location
            front_needle = Needle(True, n)
            knits[front_needle] = Instruction_Parameters(front_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)
    else:
        knits = {}
        for n in range(width-1, -1, -1):  # add extras to front
            front_needle = Needle(True, n)
            knits[front_needle] = Instruction_Parameters(front_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Right_to_Left, knits, machine_state), carriage_passes, instructions)
        knits = {}
        for n in range(0, bend_shift-width):  # add extras to back up to bend location
            back_needle = Needle(False, n)
            knits[back_needle] = Instruction_Parameters(back_needle, involved_loop=-1, carrier=c1)
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, Pass_Direction.Left_to_Right, knits, machine_state), carriage_passes, instructions)
    """
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
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                print(needle, pass_dir)
                # if at about to change dirs, do a carriage pass
                if should_switch_directions(n, width, pass_dir):
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
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                print(needle, pass_dir.opposite())
                # if at about to change dirs, do a carriage pass
                if should_switch_directions(n, width, pass_dir.opposite()):
                    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                       carriage_passes, instructions)
                    knits = {}
                    print("change dir")
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state), carriage_passes, instructions)
        print("newline")
    #instructions.append("middle")
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
    """

    n = bend_shift+width+row-height
    if n % (width * 2) < width:
        starting_dir = pass_dir.opposite()

    else:
        starting_dir = pass_dir

    pass_dir = starting_dir
    for row in range(0, height):
        knits = {}
        if row % 2 == 0:
            # even_dir
            for n in range(bend_shift+width+row-height, bend_shift-1-row+height-1, -1):  # might be wrong
                print(n)
                if n % (width * 2) < width:
                    pass_dir = starting_dir
                else:
                    pass_dir = starting_dir.opposite()
                needle = needles[n % (width*2)]
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                print(needle, pass_dir)
                # if at about to change dirs, do a carriage pass
                if should_switch_directions(n, width, pass_dir):
                    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                                       carriage_passes, instructions)
                    knits = {}
                    print("change dir")
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state),
                               carriage_passes, instructions)

        else:
            # odd_dir
            for n in range(bend_shift-row+height-1, bend_shift+width+row+1-height):  # might be wrong
                print(n)
                if n % (width * 2) < width:
                    pass_dir = starting_dir
                else:
                    pass_dir = starting_dir.opposite()
                needle = needles[n % (width*2)]
                knits[needle] = Instruction_Parameters(needle, involved_loop=-1, carrier=c1)
                print(needle, pass_dir.opposite())
                # if at about to change dirs, do a carriage pass
                if should_switch_directions(n, width, pass_dir.opposite()):
                    _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                       carriage_passes, instructions)
                    knits = {}
                    print("change dir")
            _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                               carriage_passes, instructions)
        print("newline")
    #instructions.append("done with short rows")
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
            if should_switch_directions(n, width, pass_dir.opposite()):
                _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir.opposite(), knits, machine_state),
                                   carriage_passes, instructions)
                knits = {}
        _add_carriage_pass(Carriage_Pass(Instruction_Type.Knit, pass_dir, knits, machine_state), carriage_passes, instructions)
        #instructions.append("done w posts")


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
            if bend_dir is Bend_Direction.Left:
                left_bend_helper(width, cur_bend.height, c1, machine_state, carriage_passes, instructions)
            elif bend_dir is Bend_Direction.Right:
                right_bend_helper(width, cur_bend.height, c1, machine_state, carriage_passes, instructions)
            elif bend_dir is Bend_Direction.Front:
                iso_bend_shifted_helper(width, cur_bend.height, c1, machine_state, carriage_passes, instructions, 0)
            elif bend_dir is Bend_Direction.Back:
                iso_bend_shifted_helper(width, cur_bend.height, c1, machine_state, carriage_passes, instructions, width)
            elif bend_dir >= 0 and bend_dir < circ:
                # bend starts in a particular location
                print("shifted")
                iso_bend_shifted_helper(width, cur_bend.height, c1, machine_state, carriage_passes, instructions, bend_dir)
            else:
                raise AttributeError

    # Straight part
    if end > 0:
        tube_helper(width, end, c1, machine_state, carriage_passes, instructions)

    instructions.append(outhook(machine_state, c1))
    _write_instructions(file+".k", instructions)


if __name__ == "__main__":
    #test_tube(20, 40, 3)
    #test_tube_bent(10, 40, 20, 3, True, 3)

    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Left, 3)
    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Right, 3)
    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Front, 3)
    #test_tube_bent(10, 20, 10, 4, Bend_Direction.Back, 3)
    #test_multi_bend(10, [], [], [], [], 3)
    #b1 = Bend(5, 5, Bend_Direction.Front)
    #b2 = Bend(10, 5, Bend_Direction.Back)
    #test_multi_bend(10, 3, [b1, b2], 3)
    # height is measured by full rows, short rows don't count towards height
    # some bends may have the same position
    #b3 = Bend(1, 3, 4)
    #b4 = Bend(2, 3, 9)
    #test_multi_bend(6, 3, [b3, b4], "shifted2", 3)
    #test_multi_bend(6, 3, [Bend(1, 3, 0), Bend(2, 3, 6)], "wat", 3)
    #test_multi_bend(6, 3, [Bend(1, 3, 0), Bend(2, 3, 6)], "centered", 3)
    # to knit
    #test_multi_bend(10, 5, [Bend(6, 5, 0), Bend(11, 5, 6)], "largecentered", 3)
    #test_multi_bend(10, 5, [Bend(6, 5, 4), Bend(11, 5, 9)], "largeshifted", 3)
    #test_multi_bend(10, 1, [Bend(1, 5, 0), Bend(1, 5, 6), Bend(1, 5, 0), Bend(1, 5, 6)], "consecutive", 3)
    #test_multi_bend(10, 1, [Bend(1, 5, 0), Bend(1, 5, 3), Bend(1, 5, 6), Bend(1, 5, 9)], "consecutive_shifted", 3)
    test_multi_bend(10, 5, [Bend(6, 5, 0), Bend(11, 5, 6), Bend(16, 5, 0), Bend(21, 5, 6)], "largecentered4bends", 3)
    test_multi_bend(10, 5, [Bend(11, 5, 0), Bend(16, 5, 6), Bend(26, 5, 4), Bend(31, 5, 9)], "largeshifted4bends", 3)


