from enum import Enum, auto

class StringEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __eq__(self, other):
        if isinstance(other, StringEnum):
            return super().__eq__(other)
        elif isinstance(other, str):
            return self.value == other

        return False

    def __ne__(self, other):
        return not self.__eq__(other)
