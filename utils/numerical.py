import random
import math
from typing import Union


class NumGetter:
    @classmethod
    def lt(cls, value: Union[int, float]):
        """Returns a number less than input and of the same sign."""
        if value == 0:
            lt = -1.0
        elif value > 0:
            lt = value * 0.9
        else:
            lt = value * 1.1

        if random.getrandbits(1):
            lt_int = math.floor(lt)
            if lt_int < value:
                lt = lt_int

        return lt

    @classmethod
    def lt_int(cls, value: Union[int, float]):
        """Returns an integer less than input."""
        lt = int(cls.lt(value))
        if lt >= value:
            return lt - 1
        return lt

    @classmethod
    def gt(cls, value: Union[int, float]):
        """Returns a number greater than input of the same sign."""
        if value == 0:
            gt = 1.0
        elif value > 0:
            gt = value * 1.1
        else:
            gt = value * 0.9

        if random.getrandbits(1):
            gt_int = math.ceil(gt)
            if gt_int > value:
                gt = gt_int

        return gt

    @classmethod
    def gt_int(cls, value: Union[int, float]):
        gt = int(cls.gt(value))
        if gt <= value:
            return gt + 1
        return gt
