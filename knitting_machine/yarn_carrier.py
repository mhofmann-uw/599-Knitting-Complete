from typing import Union, List


class Yarn_Carrier:
    """
    A structure to represent the location of a Yarn_carrier
    """

    def __init__(self, carrier_ids: Union[int, List[int]] = 3, position: int = -1):
        """
        Represents the state of the yarn_carriage
        :param position: the current needle position the carriage last stitched on
        :param carrier_ids: The carrier_id for this yarn
        """
        self._carrier_ids: Union[int, List[int]] = carrier_ids
        if self.many_yarns:
            for carrier in self.carrier_ids:
                assert 1 <= carrier <= 10, "Carriers must between 1 and 10"
        else:
            assert 1 <= carrier_ids <= 10, "Carriers must between 1 and 10"
        self._position: int = position

    @property
    def position(self):
        """
        :return: The current needle position the carrier is sitting at
        """
        return self._position

    @property
    def carrier_ids(self) -> Union[int, List[int]]:
        """
        :return: the id of this carrier
        """
        return self._carrier_ids

    def move_to_position(self, new_position: int):
        """
        Updates the structure as though the yarn carrier took a pass at the needle location
        :param new_position: the needle to move to
        """
        self._position = new_position

    @property
    def many_yarns(self) -> bool:
        """
        :return: True if this carrier involves multiple carriers
        """
        return type(self.carrier_ids) == list

    def not_in_operation(self, machine_state) -> list:
        not_in_operation = []
        for carrier_id in self:
            carrier = Yarn_Carrier(carrier_id)
            if carrier not in machine_state.yarns_in_operation:
                not_in_operation.append(carrier)
        return not_in_operation

    def __str__(self):
        if not self.many_yarns:
            return " " + str(self.carrier_ids)
        else:
            carriers = ""
            for carrier in self.carrier_ids:
                carriers += f" {carrier}"
            return carriers

    def __hash__(self):
        if self.many_yarns:
            hash_val = 0
            for i, carrier in enumerate(self.carrier_ids):
                hash_val += (10 ** i) * carrier  # gives unique hash for list of different orders
            return hash_val
        else:
            return self.carrier_ids

    def __eq__(self, other):
        if isinstance(other, Yarn_Carrier):
            return hash(self) == hash(other)
        return False

    def __iter__(self):
        if self.many_yarns:
            return iter(self.carrier_ids)
        else:
            return iter([self.carrier_ids])