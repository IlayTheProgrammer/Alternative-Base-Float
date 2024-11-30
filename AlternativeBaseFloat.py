import math
from copy import deepcopy
from fractions import Fraction
from typing import Iterable, Callable

STANDARD_36: dict[str:int] = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15, 'g': 16, 'h': 17, 'i': 18, 'j': 19, 'k': 20, 'l': 21, 'm': 22, 'n': 23, 'o': 24, 'p': 25, 'q': 26, 'r': 27, 's': 28, 't': 29, 'u': 30, 'v': 31, 'w': 32, 'x': 33, 'y': 34, 'z': 35}
RSTANDARD_36: dict[int:str] = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f', 16: 'g', 17: 'h', 18: 'i', 19: 'j', 20: 'k', 21: 'l', 22: 'm', 23: 'n', 24: 'o', 25: 'p', 26: 'q', 27: 'r', 28: 's', 29: 't', 30: 'u', 31: 'v', 32: 'w', 33: 'x', 34: 'y', 35: 'z'}

def decimal_parts(number: list[str], base: int, td: dict[str:int] = STANDARD_36) -> tuple[int, Fraction]:
    addMinus: bool = False

    if number[0] == '-':
        addMinus = True
        del number[0]

    ancestor_int_part: list[int] = [td[dig.lower()] if dig not in ['-', '.'] else dig for dig in number[:number.index('.')][::-1]]
    ancestor_non_int_part: list[int] = [td[dig.lower()] if dig not in ['-', '.'] else dig for dig in number[number.index('.')+1:]]

    assert max(max(ancestor_int_part), max(ancestor_non_int_part)) < base, f"The base '{base}' does not correlate to the decimal '{number}'"

    int_part: float = sum([digit * (base ** index) for index, digit in enumerate(ancestor_int_part)])
    non_int_part: Fraction = sum([digit * Fraction(1, (base ** index)) for index, digit in enumerate(ancestor_non_int_part, 1)])

    if addMinus and int_part != 0:
        int_part = -int_part

    if addMinus and non_int_part != 0:
        non_int_part = -non_int_part

    return (int_part, non_int_part)



class AlternativeBaseFloat:

    def prettified(self, formatter: dict[int:str] = RSTANDARD_36) -> str:
        """
        <p>Formates the fraction to a neat form</p>
        <h2>Parameters</h2>
        <p>&emsp;<b>formatter</b>: a dictionary to translate integer values to characters. By default is set to numbers+English alphabet</p>
        <h2>Returns</h2>
        <p>&emsp;<b>out</b>: formatted string</p>
        <h2>Examples</h2>
        ```python
        >>> x: AlternativeBaseFloat = AlternativeBaseFloat(243.5, 16)

        >>> x
        "15 3 . 8"

        >>> x.prettified()
        "f3.8[16] <== 243.5[10]"
        ```
        """
        return f"{''.join([formatter[int(dig)] if dig not in ['-', '.'] else dig for dig in self.decimal])}{'0' if self.decimal[-1] == '.' else ''}[{self.base}] <-- {''.join([formatter[int(dig)] if dig not in ['-', '.'] else dig for dig in self.ancestor_decimal])}{'0' if self.ancestor_decimal[-1] == '.' else ''}[{self.ancestor_base}]"


    def dec(self) -> float:
        """
        <p>Translates nbase float to its decimal form</p>
        <h2>Returns</h2>
        <p>&emsp;<b>out</b>: decimal float number</p>
        <h2>Examples</h2>
        ```python
        >>> x: AlternativeBaseFloat = AlternativeBaseFloat(24.5, 8)

        >>> x
        "3 0 . 4"

        >>> x.dec()
        24.5

        ```
        """

        if self.base == 10:
            return float(''.join(self.decimal))
        
        add_minus: bool = False
        number: list[str] = deepcopy(self.decimal)

        if number[0] == '-':
            add_minus = True
            del number[0]

        integer_part: list[int] = list(map(int, number[:number.index('.')][::-1]))
        non_integer_part: list[int] = list(map(int, number[number.index('.')+1:]))[::-1]

        decimal: float = sum([digit * (self.base ** index) for index, digit in enumerate(integer_part)])
        decimal += float(sum([digit * (self.base ** index) for index, digit in enumerate(non_integer_part, -len(non_integer_part))]))

        if add_minus:
            decimal = -decimal

        return float('{:.15f}'.format(decimal))


    def is_supported_by_base(self, base: int, checks: int = 7) -> bool:
        """
        <p>Checks if current decimal can be translated to another measuring system without losses</p>
        <h2>Parameters</h2>
        <p>&emsp;<b>base</b>: the base to translate to</p>
        <p>&emsp;<b>checks</>: amount of checks to do (if increased, takes more time, but the result will be more accurate). By default is set to 7</p>
        <h2>Returns</h2>
        <p>&emsp;<b>out</b>: true if the decimal can be translated with no losses, else false</p>
        <h2>Examples</h2>
        ```python
        >>> x: AlternativeBaseFloat = AlternativeBaseFloat(24.3, 10)

        >>> x.is_supported_by_base(2)
        False

        >>> x.is_supported_by_base(20)
        True
        ```
        """
        assert isinstance(base, int), f"The 'base' parameter must be of type 'int', not '{type(base)}'!"
        assert isinstance(checks, int), f"The 'checks' parameter must be of type 'int', not '{type(checks)}'!"
        assert base > 0, f"The 'base' parameter must not be less than '1' (in your case: {base} < 1)!"
        assert checks >= 0, f"The 'checks' parameter must not be less than '0' (in your case: {checks} < 0)!"

        if ''.join(self.decimal).rstrip('0') == '':
            return True
        else:
            fractionCopy: float = float(''.join(['0.', str(self.dec()).split('.')[1]]))

        while checks != 0 and "{:.15f}".format(float(fractionCopy)).split('.')[1][:-2].rstrip('0') != '':
            fractionCopy *= base
            fractionCopy = float(''.join(['0.', str(fractionCopy).split('.')[1]]))

            checks -= 1

        return checks > 0


    def converted(self, base: int) -> 'AlternativeBaseFloat':
        """
        <p>Converts current decimal to its 'base'-form</p>
        <h2>Parameters</h2>
        <p>&emsp;<b>base</b>: base to convert to</p>
        <h2>Returns</h2>
        <p>&emsp;<b>out</b>: new ABF</p>
        <h2>Examples</h2>
        ```python
        >>> x: AlternativeBaseFloat = AlternativeBaseFloat(24.5, 10)

        >>> x
        "2 4 . 5"

        >>> x.converted(2)
        "1 1 0 0 0 . 1"
        ```
        """
        assert isinstance(base, int), f"The 'base' parameter must be of type 'int', not '{type(base)}'!"
        assert base > 0, f"The 'base' parameter must not be less than '1' (in your case: {base} < 1)!"

        return AlternativeBaseFloat(self.decimal, base, self.base)


    def __format_decimal(self, number: float|int|Iterable[str]) -> list[str]:

        if isinstance(number, (float, int)):
            formatted: list[str] = list(str(float(number)))

        elif isinstance(number, str):
            formatted: list[str] = number.split(' ')

        elif isinstance(number, Iterable):
            formatted: list[str] = deepcopy(number)

        else:
            raise ValueError(f"The 'number' parameter must be either an iterable of strings, a float or an int, not {type(number)}")
        
        if '.' not in formatted:
            formatted.extend(['.', '0'])

        elif formatted == ['.']:
            formatted: list[str] = ['0', '.', '0']

        elif '.' == formatted[-1]:
            formatted.append('0')

        return formatted


    def __convert_int_part(self, number: int, base: int) -> list[int]:
        result: list[int] = []

        while number // base != 0:
            result.append(number % self.base)
            number //= self.base

        if number != 0:
            result.append(number)

        if result == []:
            result.append(0)

        return result[::-1]


    def __convert_float_part(self, decimal: Fraction, base: int) -> list[int]:
        result: list[int] = []
        max_digits: int = 15
        decimal: float = float(decimal)

        __has_tail: Callable = lambda decimal: "{:.15f}".format(decimal).split('.')[1][:-2].rstrip('0') != ''
        __from_scientific_notation_to_float: Callable = lambda decimal: float("{:.15f}".format(decimal).rstrip('0'))
        __nullify: Callable = lambda decimal: float(''.join(['0.', str(decimal).split('.')[1]]))

        while max_digits != 0 and __has_tail(decimal):
            decimal *= base

            decimal: float = __from_scientific_notation_to_float(decimal)
            result.append(int(str(decimal).split('.')[0]))

            decimal: float = __from_scientific_notation_to_float(__nullify(decimal))

            max_digits -= 1

        if result == []:
            result.append(0)

        del decimal
        del max_digits
        del __has_tail
        del __from_scientific_notation_to_float
        del __nullify

        return result


    def __init__(self, number: float|int|Iterable[str], base_to_convert_to: int, base_to_convert_from: int = 10) -> None:
        """
        <p>A class to create float numbers of non-standard bases</p>
        <h2>Parameters</h2>
        <p>&emsp;<b>number</b>: the number to translate</p>
        <p>&emsp;<b>base_to_convert_to</b>: base to convert the number to</p>
        <p>&emsp;<b>base_to_convert_from</b>: base to convert the number from</p>
        <h2>Used Modules</h2>
        <p>&emsp;<b>math</b> for 'lcm()' and 'trunc()' function</p>
        <p>&emsp;<b>copy</b> for the 'deepcopy()' function</p>
        <p>&emsp;<b>fractions</b> for the class 'Fraction' and its methods</p>
        <p>&emsp;<b>typing</b> for the classes 'Iterable' and 'Callable'</p>
        """
        assert isinstance(base_to_convert_to, int), f"The 'base_to_convert_to' parameter must be of type 'int', not '{type(base_to_convert_to)}'!"
        assert isinstance(base_to_convert_from, int), f"The 'base_to_convert_from' parameter must be of type 'int', not '{type(base_to_convert_from)}'!"
        assert base_to_convert_to > 0, f"The 'base_to_convert_to' parameter must be greater than zero ({base_to_convert_to} < 1)!"
        assert base_to_convert_from > 0, f"The 'base_to_convert_from' parameter must be greater than zero ({base_to_convert_from} < 1)!"

        self.base: int = base_to_convert_to

        self.ancestor_decimal: list[str] = self.__format_decimal(number)
        self.ancestor_base: int = base_to_convert_from

        if self.base == self.ancestor_base:
            self.decimal: list[str] = deepcopy(self.ancestor_decimal)
        else:
            ad_integer_part, ad_non_integer_part = decimal_parts(self.ancestor_decimal, self.ancestor_base)

            add_minus: bool = False
            if str(ad_integer_part)[0] == '-':
                add_minus = True
                ad_integer_part: int = -ad_integer_part

            if str(ad_non_integer_part)[0] == '-':
                add_minus = True
                ad_non_integer_part: Fraction = -ad_non_integer_part

            integer_part: list[int] = self.__convert_int_part(ad_integer_part, self.base)
            non_integer_part: list[int] = self.__convert_float_part(ad_non_integer_part, self.base)

            del ad_integer_part
            del ad_non_integer_part

            decimal: list[str] = []

            if add_minus:
                decimal.append('-')

            del add_minus

            decimal.extend(list(map(str, integer_part)))
            decimal.append('.')
            decimal.extend(list(map(str, non_integer_part)))

            del integer_part
            del non_integer_part

            self.decimal: list[str] = decimal


    def __str__(self) -> str:
        return f"{' '.join(self.decimal)}"


    def __repr__(self) -> str:
        return f"{'/'.join(self.decimal) if self.base > 10 else ''.join(self.decimal)}[{self.base}] <-- {'/'.join(self.ancestor_decimal) if self.ancestor_base > 10 else ''.join(self.ancestor_decimal)}[{self.ancestor_base}]"


    def __int__(self) -> int:
        return math.trunc(self.dec())


    def __float__(self) -> float:
        return self.dec()


    def __ceil__(self) -> 'AlternativeBaseFloat':

        if ''.join(self.decimal)[self.decimal.index('.'):].rstrip('0') != '.':
            return self.__trunc__() + 1
        
        else:
            return self


    def __floor__(self) -> 'AlternativeBaseFloat':

        if ''.join(self.decimal)[self.decimal.index('.'):].rstrip('0') != '.':
            return self.__trunc__()
        
        else:
            return self


    def __trunc__(self) -> 'AlternativeBaseFloat':
        return AlternativeBaseFloat(' '.join([*self.decimal[:self.decimal.index('.')], '. 0']), self.base, self.base)


    def __round__(self, digits: int) -> 'AlternativeBaseFloat':
        result: list[str] = self.decimal[:self.decimal.index('.')+1]

        for i in self.decimal[self.decimal.index('.')+1:]:
            result.append(i)
            digits -= 1

            if digits <= 0:
                break

        return AlternativeBaseFloat(result, self.base, self.base)


    def __add__(self, other) -> 'AlternativeBaseFloat':

        assert isinstance(other, (int, float, AlternativeBaseFloat)), f"To add a variable to an instance of the ABF class, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        if isinstance(other, (int, float)):
            other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)

        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) + sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp
    

    def __sub__(self, other) -> 'AlternativeBaseFloat':
        
        assert isinstance(other, (int, float, AlternativeBaseFloat)), f"To subtract a variable from an instance of the ABF class, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        if isinstance(other, (int, float)):
            other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)

        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) - sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp


    def __mul__(self, other) -> 'AlternativeBaseFloat':

        assert isinstance(other, (int, float, AlternativeBaseFloat)), f"To multiply an instance of the ABF class by a variable, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        if isinstance(other, (int, float)):
            other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)

        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) * sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp


    def __truediv__(self, other) -> 'AlternativeBaseFloat':

        assert isinstance(other, (int, float, AlternativeBaseFloat)), f"To divide an instance of the ABF class by a variable, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        if isinstance(other, (int, float)):
            other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)

        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) / sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp


    def __pow__(self, other) -> 'AlternativeBaseFloat':

        assert isinstance(other, int), f"To raise an instance of the ABF class to a variable, the variable must be of type 'int', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) ** sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp


    def __floordiv__(self, other) -> 'AlternativeBaseFloat':

        assert isinstance(other, (int, float, AlternativeBaseFloat)), f"To divide and floor an instance of the ABF class by a variable, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        if isinstance(other, (int, float)):
            other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)

        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) // sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp


    def __mod__(self, other) -> 'AlternativeBaseFloat':

        assert isinstance(other, (int, float, AlternativeBaseFloat)), f"To get a modulus of an instance of the ABF class divided by a variable, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        if isinstance(other, (int, float)):
            other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)

        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) % sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = self.base
        temp.ancestor_decimal = self.decimal

        return temp


    def __radd__(self, other) -> 'AlternativeBaseFloat':
        assert isinstance(other, (int, float)), f"To add an instance of the ABF class to a variable, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) + sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = other.base
        temp.ancestor_decimal = other.decimal

        return temp


    def __rsub__(self, other) -> 'AlternativeBaseFloat':
        assert isinstance(other, (int, float)), f"To subtract an instance of the ABF class from a variable, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) - sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = other.base
        temp.ancestor_decimal = other.decimal

        return temp


    def __rmul__(self, other) -> 'AlternativeBaseFloat':
        assert isinstance(other, (int, float)), f"To multiply a variable by an instance of the ABF class, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) * sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = other.base
        temp.ancestor_decimal = other.decimal

        return temp


    def __rtruediv__(self, other) -> 'AlternativeBaseFloat':
        assert isinstance(other, (int, float)), f"To divide a variable by an instance of the ABF class, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) / sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = other.base
        temp.ancestor_decimal = other.decimal

        return temp


    def __rfloordiv__(self, other) -> 'AlternativeBaseFloat':
        assert isinstance(other, (int, float)), f"To divide and floor a variable by an instance of the ABF class, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) + sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = other.base
        temp.ancestor_decimal = other.decimal

        return temp


    def __rmod__(self, other) -> 'AlternativeBaseFloat':
        assert isinstance(other, (int, float)), f"To get a modulus of a variable divided by an instance of the ABF class, the variable must be either of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'!"

        other: 'AlternativeBaseFloat' = AlternativeBaseFloat(float(other), 10)
        mutual_base: int = math.lcm(self.base, other.base)
        converted_self, converted_other = self.converted(mutual_base), other.converted(mutual_base)
        result: Fraction = sum(decimal_parts(converted_self.decimal, mutual_base)) % sum(decimal_parts(converted_other.decimal, mutual_base))
        
        temp: AlternativeBaseFloat = AlternativeBaseFloat(float(result), mutual_base)
        temp.ancestor_base = other.base
        temp.ancestor_decimal = other.decimal

        return temp


    def __iadd__(self, other) -> None:
        temp: AlternativeBaseFloat = self + other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __isub__(self, other) -> None:
        temp: AlternativeBaseFloat = self - other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __imul__(self, other) -> None:
        temp: AlternativeBaseFloat = self * other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __itruediv__(self, other) -> None:
        temp: AlternativeBaseFloat = self / other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __ipow__(self, other) -> None:
        temp: AlternativeBaseFloat = self ** other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __imod__(self, other) -> None:
        temp: AlternativeBaseFloat = self % other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __ifloordiv__(self, other) -> None:
        temp: AlternativeBaseFloat = self // other

        self.ancestor_decimal = self.decimal
        self.ancestor_decimal = self.base
        self.decimal = temp.decimal
        self.base = temp.base

        return self


    def __neg__(self) -> 'AlternativeBaseFloat':
        result: AlternativeBaseFloat = AlternativeBaseFloat(' '.join(['-', *self.decimal]), self.base, self.base) if self.decimal[0] != '-' else AlternativeBaseFloat(self.decimal[1:], self.base, self.base)
        result.ancestor_decimal = self.decimal

        return result


    def __abs__(self) -> 'AlternativeBaseFloat':
        result: AlternativeBaseFloat = AlternativeBaseFloat(self.decimal[1:], self.base, self.base) if self.decimal[0] == '-' else self
        result.ancestor_decimal = self.decimal

        return result
 

    def __pos__(self) -> 'AlternativeBaseFloat':
        return self


    def __gt__(self, other) -> bool:

        if isinstance(other, AlternativeBaseFloat):
            return self.dec() > other.dec()
        
        elif isinstance(other, (float, int)):
            return self.dec() > other
        
        else:
            raise ValueError(f"To compare a variable to an instance of the ABF class it must either be of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'")


    def __ge__(self, other) -> bool:
        return (self > other) or (self == other)


    def __lt__(self, other) -> bool:

        if isinstance(other, AlternativeBaseFloat):
            return self.dec() < other.dec()
        
        elif isinstance(other, (float, int)):
            return self.dec() < other
        
        else:
            raise ValueError(f"To compare a variable to an instance of the ABF class it must either be of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'")


    def __le__(self, other) -> bool:
        return (self < other) or (self == other)


    def __eq__(self, other) -> bool:

        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)
            return self.converted(mutualBase).decimal == other.converted(mutualBase).decimal
        
        elif isinstance(other, (float, int)):
            mutualBase: int = math.lcm(self.base, 10)
            otherObj: AlternativeBaseFloat = AlternativeBaseFloat(float(other), mutualBase)
            return self.converted(mutualBase).decimal == otherObj.decimal
        
        else:
            raise ValueError(f"To compare a variable to an instance of the ABF class it must either be of type 'int', 'float', or 'AlternativeBaseFloat', not '{type(other)}'")


    def __ne__(self, other) -> bool:
        return not (self == other)





