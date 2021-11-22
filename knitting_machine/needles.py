class Needle:
    """
    A Simple class structure for keeping track of needle locations
    """

    def __init__(self, is_front: bool, position: int):
        """
        :param is_front: True if front bed needle, False otherwise
        :param position: the needle index of this needle
        """
        self.is_front: bool = is_front
        self.position: int = position
        assert self.position is not None

    @property
    def is_back(self) -> bool:
        """
        :return: True if needle is a back needle
        """
        return not self.is_front

    def opposite(self, slider: bool = False):
        """
        :param slider: If true, creates a slider needle
        :return: the needle on the opposite bed at the same position
        """
        if slider:
            return Slider_Needle(is_front=not self.is_front, position=self.position)
        else:
            return Needle(is_front=not self.is_front, position=self.position)

    def offset(self, offset: int, slider: bool = False):
        """
        :param slider: If true, creates a slider needle
        :param offset: the amount to offset the needle from
        :return: the needle offset spaces away on the same bed
        """
        if slider:
            return Slider_Needle(is_front=self.is_front, position=self.position + offset)
        else:
            return Needle(is_front=self.is_front, position=self.position + offset)

    def slider(self):
        """
        :return: The slider needle at this position
        """
        return Slider_Needle(is_front=self.is_front, position=self.position)

    def main_needle(self):
        """
        :return: The non-slider needle at this needle positions
        """
        return Needle(is_front= self.is_front, position=self.position)

    def __str__(self):
        if self.is_front:
            return f"f{self.position + 1}"
        else:
            return f"b{self.position + 1}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.position

    def __lt__(self, other):
        if isinstance(other, Needle):
            return self.position < other.position
        elif type(other) is int:
            return self.position < other
        else:
            raise AttributeError

    @property
    def is_slider(self) -> bool:
        """
        :return: True if the needle is a slider
        """
        return False

    def is_clear(self, machine_state) -> bool:
        """
        a needle is clear if it is a sliding needle or if its associated slider needle is empty
        :param machine_state: used to get slider needle
        :return: True if needle is clear
        """
        slider = self.slider()
        slider_loops = machine_state[slider]
        return len(slider_loops) == 0


class Slider_Needle(Needle):
    """
    A Needle subclass for slider needles which an only transfer loops, but not be knit through
    """

    def __init__(self, is_front: bool, position: int):
        super().__init__(is_front, position)

    def __str__(self):
        if self.is_front:
            return f"fs{self.position + 1}"
        else:
            return f"bs{self.position + 1}"

    @property
    def is_slider(self) -> bool:
        """
        :return: True if the needle is a slider
        """
        return True

    def is_clear(self, machine_state):
        """
        a needle is clear if it is a sliding needle or if its associated slider needle is empty
        :param machine_state: not used by slider
        :return: True if needle is clear
        """
        return True