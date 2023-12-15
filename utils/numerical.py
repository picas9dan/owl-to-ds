import random
import math
from typing import Union

from constants.functions import NumOp


class NumGetter:
    @classmethod
    def lt(cls, value: Union[int, float], returns_int: bool = False):
        """Returns a number less than input and of the same sign."""
        if value == 0:
            lt = -1.0
        elif value > 0:
            lt = value * 0.9
        else:
            lt = value * 1.1

        if returns_int or random.getrandbits(1):
            lt = math.floor(lt)
            if lt == value:
                lt = value - 1

        assert lt < value, value
        assert lt * value >= 0, value
        return lt

    @classmethod
    def gt(cls, value: Union[int, float], returns_int: bool = False):
        """Returns a number greater than input of the same sign."""
        if value == 0:
            gt = 1.0
        elif value > 0:
            gt = value * 1.1
        else:
            gt = value * 0.9

        if returns_int or random.getrandbits(1):
            gt = math.ceil(gt)
            if gt == value:
                gt = value + 1

        assert gt > value, value
        assert gt * value >= 0, value
        return gt


def make_operand_and_verbn(operator: NumOp, value: Union[int, float], returns_int: bool=False):
    if operator == NumOp.LESS_THAN:
        operand = NumGetter.gt(value, returns_int=returns_int)
        verbn = random.choice(["<", "less than", "lower than", "smaller than"])
    elif operator == NumOp.LESS_THAN_EQUAL:
        if random.getrandbits(1):
            operand = NumGetter.gt(value, returns_int=returns_int)
        else:
            operand = value
        verbn = random.choice(["<=", "less than or equal to", "not greater than"])
    elif operator == NumOp.GREATER_THAN:
        operand = NumGetter.lt(value, returns_int=returns_int)
        verbn = random.choice([">", "greater than", "higher than", "bigger than"])
    elif operator == NumOp.GREATER_THAN_EQUAL:
        if random.getrandbits(1):
            operand = NumGetter.lt(value, returns_int=returns_int)
        else:
            operand = value
        verbn = random.choice([">=", "greater than or equal to", "not less than"])
    elif operator == NumOp.EQUAL:
        operand = value
        verbn = random.choice(["=", "equal to"])
    else:
        raise ValueError("Unexpected operator: " + str(operator))
    
    verbn += " " + str(operand)

    return operand, verbn
