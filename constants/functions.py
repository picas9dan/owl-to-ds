from enum import Enum


class NumOp(Enum):
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_EQUAL = "<="
    GREATER_THAN_EQUAL = ">="
    EQUAL = "="
    AROUND = "around"
    INSIDE_RANGE = "in"
    OUTSIDE_RANGE = "outside"

PRIMITIVE_NUM_OPS = [NumOp.LESS_THAN, NumOp.GREATER_THAN, NumOp.LESS_THAN_EQUAL, NumOp.GREATER_THAN_EQUAL, NumOp.EQUAL]

class StrOp(Enum):
    VALUES = "values"
