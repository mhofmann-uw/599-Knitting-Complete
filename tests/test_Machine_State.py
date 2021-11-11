from knitting_machine.Machine_State import Machine_State, Pass_Direction, Needle, Yarn_Carrier
from knitting_machine.operation_sets import Carriage_Pass, Instruction_Type


def test_platting():
    machine_state = Machine_State()
    carriage_passes = []
    c1 = Yarn_Carrier(3)
    c2 = Yarn_Carrier(4)

    # Cast on
    tuck_lr = {}
    for i in range(20, 2, -1):
        tuck_lr[Needle(True, i)] = (-1, None)
    carriage_pass= Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Left_to_Right, tuck_lr, [c1], machine_state)

    tuck_rl = {}
    for i in range(1, 19):
        tuck_rl[Needle(True, i)] = (-1, None)
    carriage_pass= Carriage_Pass(Instruction_Type.Tuck, Pass_Direction.Right_to_Left, tuck_rl, [c1], machine_state)


