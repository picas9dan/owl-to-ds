from decimal import Decimal
import random
import math
from typing import Optional

from constants.functions import NumOp


class NumGetter:
    @classmethod
    def lt(
        cls,
        value: Decimal,
        to_int: bool = False,
        min_val: Optional[Decimal] = None,
    ):
        """Returns a number less than input and of the same sign."""
        if min_val is not None and value < min_val:
            raise ValueError(
                "Unable to generate a number less than {val} but no less than {min}".format(
                    val=value, min=min_val
                )
            )

        if value == Decimal('0'):
            lt = Decimal('-1.0')
        elif value > Decimal('0'):
            lt = value * Decimal('0.9')
        else:
            lt = value * Decimal('1.1')

        if to_int or random.getrandbits(1):
            lt = math.floor(lt)
            if lt == value:
                lt = value - Decimal('1')

        lt = max(lt, min_val)

        assert lt < value, value
        assert lt * value >= Decimal('0'), value
        return lt

    @classmethod
    def gt(
        cls,
        value: Decimal,
        to_int: bool = False,
        max_val: Optional[Decimal] = None,
    ):
        """Returns a number greater than input of the same sign."""
        if value > max_val:
            raise ValueError(
                "Unable to generate a number greater than {value} but no greater than {max}".format(
                    value=value, max=max_val
                )
            )

        if value == Decimal('0'):
            gt = Decimal('1.0')
        elif value > Decimal('0'):
            gt = value * Decimal('1.1')
        else:
            gt = value * Decimal('0.9')

        if to_int or random.getrandbits(1):
            gt = math.ceil(gt)
            if gt == value:
                gt = value + Decimal('1')

        gt = min(gt, max_val)

        assert gt > value, value
        assert gt * value >= Decimal('0'), value
        return gt



def make_operand_and_verbn(
    operator: NumOp,
    value: Decimal,
    to_int: bool = False,
    max_val: Optional[Decimal] = None,
    min_val: Optional[Decimal] = None,
):
    if operator == NumOp.LESS_THAN:
        operand = NumGetter.gt(value, to_int=to_int, max_val=max_val)
        verbn = random.choice(["<", "less than", "lower than", "smaller than"])
    elif operator == NumOp.LESS_THAN_EQUAL:
        if random.getrandbits(1):
            operand = NumGetter.gt(value, to_int=to_int, max_val=max_val)
        else:
            operand = value
        verbn = random.choice(["<=", "less than or equal to", "not greater than"])
    elif operator == NumOp.GREATER_THAN:
        operand = NumGetter.lt(value, to_int=to_int, min_val=min_val)
        verbn = random.choice([">", "greater than", "higher than", "bigger than"])
    elif operator == NumOp.GREATER_THAN_EQUAL:
        if random.getrandbits(1):
            operand = NumGetter.lt(value, to_int=to_int, min_val=min_val)
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
