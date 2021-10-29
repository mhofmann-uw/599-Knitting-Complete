"""Symbol Table structure holds definitions of stitches and context for number variables"""
from typing import Dict, Union

from knit_graphs.Knit_Graph import Pull_Direction
from knitspeak_compiler.knitspeak_interpreter.cable_definitions import Cable_Definition
from knitspeak_compiler.knitspeak_interpreter.stitch_definitions import Stitch_Definition, Stitch_Lean


class Symbol_Table:
    """
    A class used to keep track of how stitches and number variables have been defined. Includes language defaults
    """

    def __init__(self):
        self._symbol_table: Dict[str, Union[Cable_Definition, Stitch_Definition, int]] = {"k": self._knit(), "p": self._purl(),
                                                                                         "yo": self._yo(), "slip": self._slip()}
        self._decreases()
        self._cables()
        # set current row variable
        self._symbol_table["current_row"] = 0

    def _cables(self):
        # Todo: Add cable symbols keyed to their definitions to the symbol table
        #  (i.e., self._symbol_table[{cable_name}] = Cable_Definition(...))
        #  for every combination of right and left loop counts create cables that:
        #   lean left, lean right, lean left and purl, lean right and purl,
        #  e.g. for 1 left stitch and 2 right stitches you will have:
        #   LC1|2, LC1P|2, LC1|2P, LC1P|2P, RC1|2, RC1P|2, RC1|2P, RC1P|2P
        #  each group of loops can have 1, 2, or 3 loops
        for l in [1, 2, 3]:
            for r in [1, 2, 3]:
                # cables of the form: {L|R}C{#left crossing loops}{purl left crossing loops}?|{#right crossing loops}{purl right crossing loops}?
                self[f"LC{l}|{r}"] = Cable_Definition(l, r, cable_lean=Stitch_Lean.Left)
                self[f"RC{l}|{r}"] = Cable_Definition(l, r, cable_lean=Stitch_Lean.Right)
                self[f"LC{l}P|{r}"] = Cable_Definition(l, r,
                                                       left_crossing_pull_direction=Pull_Direction.FtB,
                                                       cable_lean=Stitch_Lean.Left)
                self[f"RC{l}P|{r}"] = Cable_Definition(l, r,
                                                       left_crossing_pull_direction=Pull_Direction.FtB,
                                                       cable_lean=Stitch_Lean.Right)
                self[f"LC{l}P|{r}P"] = Cable_Definition(l, r,
                                                        left_crossing_pull_direction=Pull_Direction.FtB,
                                                        right_crossing_pull_direction=Pull_Direction.FtB,
                                                        cable_lean=Stitch_Lean.Left)
                self[f"RC{l}P|{r}P"] = Cable_Definition(l, r,
                                                        left_crossing_pull_direction=Pull_Direction.FtB,
                                                        right_crossing_pull_direction=Pull_Direction.FtB,
                                                        cable_lean=Stitch_Lean.Right)
                self[f"LC{l}|{r}P"] = Cable_Definition(l, r,
                                                       right_crossing_pull_direction=Pull_Direction.FtB,
                                                       cable_lean=Stitch_Lean.Left)
                self[f"RC{l}|{r}P"] = Cable_Definition(l, r,
                                                       right_crossing_pull_direction=Pull_Direction.FtB,
                                                       cable_lean=Stitch_Lean.Right)

    def _decreases(self):
        # Todo: add decrease symbols keyed to their definitions to the symbol table
        #  (i.e., self[{stitch_name}] = Stitch_Definition(...))
        #  You need to implement the following stitches: k2tog,k3tog, p2tog, p3tog,
        #   skpo,sppo (purl version of skpo), s2kpo, s2ppo, sk2po, sp2po
        for n in [2, 3]:  # ntog
            offsets = [offset * -1 for offset in range(n - 1, -1, -1)]
            self[f"k{n}tog"] = Stitch_Definition(offset_to_parent_loops=offsets)
            self[f"p{n}tog"] = Stitch_Definition(Pull_Direction.FtB, offset_to_parent_loops=offsets)
        for n in [1, 2]:
            offsets = [offset for offset in range(0, n + 1)]
            k = ""
            if n >= 2:
                k = str(n)
            self[f"s{k}kpo"] = Stitch_Definition(offset_to_parent_loops=offsets)
            self[f"s{k}ppo"] = Stitch_Definition(Pull_Direction.FtB, offset_to_parent_loops=offsets)
        self["sk2po"] = Stitch_Definition(offset_to_parent_loops=[-1, 0, 1])
        self["sp2po"] = Stitch_Definition(Pull_Direction.FtB, offset_to_parent_loops=[-1, 0, 1])

    @staticmethod
    def _slip() -> Stitch_Definition:
        # Todo: Return (in one line) a Stitch Definition with no child_loops
        return Stitch_Definition(child_loops=0)

    @staticmethod
    def _yo() -> Stitch_Definition:
        # Todo: Return (in one line) will create a new loop with no parents
        return Stitch_Definition(offset_to_parent_loops=[])

    @staticmethod
    def _purl() -> Stitch_Definition:
        # Todo: Return (in one line) a Stitch Definition that will purl the next available loop
        return Stitch_Definition(pull_direction=Pull_Direction.FtB)

    @staticmethod
    def _knit() -> Stitch_Definition:
        # Todo: Return (in one line) a Stitch Definition that will knit the next available loop
        return Stitch_Definition()

    def __contains__(self, item: str):
        return item.lower() in self._symbol_table

    def __setitem__(self, key: str, value: Union[int, Stitch_Definition, Cable_Definition]):
        self._symbol_table[key.lower()] = value

    def __getitem__(self, item: str):
        return self._symbol_table[item.lower()]
