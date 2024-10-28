import math
from copy import deepcopy
from fractions import Fraction
from typing import Iterable



def breakIntoDecParts(number: list[str], base: int) -> tuple[int, Fraction]:
    addMinus: bool = False

    if number[0] == '-':
        addMinus = True
        del number[0]

    ancestorIntegerPart: list[int] = list(map(int, number[:number.index('.')][::-1]))

    ancestorFractionalPart: list[int] = list(map(int, number[number.index('.')+1:]))

    assert max(max(ancestorIntegerPart), max(ancestorFractionalPart)) < base, f"The base '{base}' does not correlate to the decimal '{number}'"

    integerDecimalPart: float = sum([digit * (base ** index) for index, digit in enumerate(ancestorIntegerPart)])
    fractionalDecimalPart: Fraction = sum([digit * Fraction(1, (base ** index)) for index, digit in enumerate(ancestorFractionalPart, 1)])

    if addMinus and integerDecimalPart != 0:
        integerDecimalPart = -integerDecimalPart

    elif addMinus and fractionalDecimalPart != 0:
        fractionalDecimalPart = -fractionalDecimalPart

    return (integerDecimalPart, fractionalDecimalPart)
