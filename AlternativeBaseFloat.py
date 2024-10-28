from System_functional import *



class AlternativeBaseFloat:

    def getInfo(self) -> tuple[list[str], int, list[str], int]:
        return (self.decimal, self.base, self.ancestorDecimal, self.ancestorBase)

    def prettified(self) -> str:
        return f"{'/'.join(self.decimal) if self.base > 10 else ''.join(self.decimal)}{'0' if self.decimal[-1] == '.' else ''}[{self.base}] <-- {'/'.join(self.ancestorDecimal) if self.ancestorBase > 10 else ''.join(self.ancestorDecimal)}{'0' if self.ancestorDecimal[-1] == '.' else ''}[{self.ancestorBase}]"
    
    def dec(self) -> float:
        addMinus: bool = False
        number: list[str] = self.decimal

        if number[0] == '-':
            addMinus = True
            del number[0]

        integerPart: list[int] = list(map(int, number[:number.index('.')][::-1]))

        fractionalPart: list[int] = list(map(int, number[number.index('.')+1:]))[::-1]

        decimalNumber: float = sum([digit * (self.base ** index) for index, digit in enumerate(integerPart)])

        decimalNumber += float(sum([digit * (self.base ** index) for index, digit in enumerate(fractionalPart, -len(fractionalPart))]))

        if addMinus:
            decimalNumber = -decimalNumber

        return float('{:.14f}'.format(decimalNumber))

    def isSupportedByBase(self, base: int, checks: int = 7) -> bool:

        if ''.join(self.decimal).rstrip('0') == '':
            return True
        
        else:
            fractionCopy = float(''.join(['0.', str(self.dec()).split('.')[1]]))

        while checks != 0 and "{:.14f}".format(float(fractionCopy)).split('.')[1][:-2].rstrip('0') != '':
            fractionCopy *= base
            fractionCopy = float(''.join(['0.', str(fractionCopy).split('.')[1]]))

            checks -= 1

        return checks > 0

    def converted(self, base: int) -> 'AlternativeBaseFloat':
        return AlternativeBaseFloat(self.decimal, base, self.base)

    def formatDecimal(self, number: float|int|Iterable[str]) -> list[str]:

        if isinstance(number, (float, int)):
            ancestorDecimal: list[str] = list(str(float(number)))

        elif isinstance(number, str):
            ancestorDecimal: list[str] = number.split(' ')

        elif isinstance(number, Iterable):
            ancestorDecimal: list[str] = deepcopy(number)

        else:
            raise ValueError('Input number must be either an iterable of string type, float or int number')
        
        if '.' not in ancestorDecimal:
            ancestorDecimal.extend(['.', '0'])

        elif ancestorDecimal == ['.']:
            ancestorDecimal = ['0', '.', '0']

        elif '.' == ancestorDecimal[-1]:
            ancestorDecimal.append('0')

        return ancestorDecimal



    def __init__(self, number: float|int|Iterable[str], baseToConvertTo: int, baseToConvertFrom: int = 10) -> None:

        self.base: int = baseToConvertTo

        self.ancestorDecimal: list[str] = deepcopy(self.formatDecimal(number))

        self.ancestorBase: int = baseToConvertFrom

        ancestorIntegerPart, ancestorFractionalPart = breakIntoDecParts(self.ancestorDecimal, self.ancestorBase)

        precision: int = 15
        temporaryInt: list[int] = []
        temporaryFraction: list[int] = []

        addMinus: bool = False

        if str(ancestorIntegerPart)[0] == '-':
            addMinus = True
            ancestorIntegerPart = -ancestorIntegerPart

        elif str(ancestorFractionalPart)[0] == '-':
            addMinus = True
            ancestorFractionalPart = -ancestorFractionalPart

        while ancestorIntegerPart // self.base != 0:
            temporaryInt.append(ancestorIntegerPart % self.base)
            ancestorIntegerPart //= self.base

        temporaryInt.append(ancestorIntegerPart)
        temporaryInt = temporaryInt[::-1]

        while precision != 0 and "{:.14f}".format(float(ancestorFractionalPart)).split('.')[1][:-2].rstrip('0') != '':
            ancestorFractionalPart = float(ancestorFractionalPart)
            ancestorFractionalPart *= self.base
            ancestorFractionalPart = float("{:.14f}".format(ancestorFractionalPart).rstrip('0'))

            temporaryFraction.append(int(str(ancestorFractionalPart).split('.')[0]))
            ancestorFractionalPart = float(''.join(['0.', str(ancestorFractionalPart).split('.')[1]]))

            ancestorFractionalPart = "{:.14f}".format(float(str(ancestorFractionalPart)))

            precision -= 1

        if temporaryFraction == []:
            temporaryFraction.append('0')

        decimal: list[str] = []

        if addMinus:
            decimal.append('-')     

        decimal.extend(list(map(str, temporaryInt)))
        decimal.append('.')
        decimal.extend(list(map(str, temporaryFraction))) 
        self.decimal = decimal



    def __str__(self) -> str:
        return f"{' '.join(self.decimal)}"
    
    def __repr__(self) -> str:
        return f"{'/'.join(self.decimal) if self.base > 10 else ''.join(self.decimal)}[{self.base}] <-- {'/'.join(self.ancestorDecimal) if self.ancestorBase > 10 else ''.join(self.ancestorDecimal)}[{self.ancestorBase}]"

    def __int__(self) -> int:
        return math.trunc(self.dec())

    def __float__(self) -> float:
        return self.dec()



    def __ceil__(self) -> 'AlternativeBaseFloat':

        if ''.join(self.decimal)[self.decimal.index('.'):].rstrip('0') != '.':

            return self.__trunc__() + 1
                
        else:
            return self.converted(self.base)

    def __floor__(self) -> 'AlternativeBaseFloat':

        if ''.join(self.decimal)[self.decimal.index('.'):].rstrip('0') != '.':
            return self.__trunc__()

        else:
            return self.converted(self.base)

    def __trunc__(self) -> 'AlternativeBaseFloat':
        return AlternativeBaseFloat(' '.join([' '.join(self.decimal[:self.decimal.index('.')]), '. 0']), self.base, self.base)

    def __round__(self, digits: int) -> 'AlternativeBaseFloat':
        temporary: list[str] = self.decimal[:self.decimal.index('.')+1]

        for i in self.decimal[self.decimal.index('.')+1:]:
            temporary.append(i)
            digits -= 1

            if digits <= 0:
                break

        return AlternativeBaseFloat(temporary, self.base, self.base)



    def __add__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, AlternativeBaseFloat):      
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) + sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)


        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)

            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase), otherObj.converted(mutualBase)

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) + sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)


        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
    
    def __sub__(self, other) -> 'AlternativeBaseFloat':
        
        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) - sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)


        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)

            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase), otherObj.converted(mutualBase)

            del otherObj

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) - sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)


        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
    
    def __mul__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) * sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase), otherObj.converted(mutualBase)

            del otherObj

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) * sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')

    def __truediv__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) / sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) / sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')

    def __pow__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) ** sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) ** sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')

    def __floordiv__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) // sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) // sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')

    def __mod__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, AlternativeBaseFloat):
            mutualBase: int = math.lcm(self.base, other.base)

            convertedSelf, convertedOther = self.converted(mutualBase), other.converted(mutualBase)
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) % sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        elif isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) % sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
        


    def __radd__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)

            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase), otherObj.converted(mutualBase)

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) + sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)


        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
    
    def __rsub__(self, other) -> 'AlternativeBaseFloat':
        
        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)

            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase), otherObj.converted(mutualBase)

            del otherObj

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) - sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)


        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
    
    def __rmul__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase), otherObj.converted(mutualBase)

            del otherObj

            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) * sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')

    def __rtruediv__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) / sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')

    def __rpow__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) ** sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
    
    def __rfloordiv__(self, other) -> 'AlternativeBaseFloat':

        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) // sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
        
    def __rmod__(self, other) -> 'AlternativeBaseFloat':
        if isinstance(other, (int, float)):
            otherObj = AlternativeBaseFloat(float(other), 10)
            
            mutualBase: int = math.lcm(self.base, otherObj.base)

            convertedSelf, convertedOther = self.converted(mutualBase).decimal, otherObj.converted(mutualBase).decimal

            del otherObj
            
            result: Fraction = sum(breakIntoDecParts(convertedSelf.decimal, mutualBase)) % sum(breakIntoDecParts(convertedOther.decimal, mutualBase))
            
            return AlternativeBaseFloat(float(result), mutualBase)
        

        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')



    def __iadd__(self, other) -> None:
        temp: AlternativeBaseFloat = self + other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self
    
    def __isub__(self, other) -> None:
        temp: AlternativeBaseFloat = self - other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self
    
    def __imul__(self, other) -> None:
        temp: AlternativeBaseFloat = self * other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self
    
    def __itruediv__(self, other) -> None:
        temp: AlternativeBaseFloat = self / other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self
    
    def __ipow__(self, other) -> None:
        temp: AlternativeBaseFloat = self ** other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self
    
    def __imod__(self, other) -> None:
        temp: AlternativeBaseFloat = self % other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self
    
    def __ifloordiv__(self, other) -> None:
        temp: AlternativeBaseFloat = self // other

        self.ancestorDecimal = self.decimal
        self.ancestorDecimal = self.base

        self.decimal = temp.decimal
        self.base = temp.base

        return self



    def __neg__(self) -> 'AlternativeBaseFloat':
        decimalCopy: list[str] = deepcopy(self.decimal)

        if self.decimal[0] != '-':
            decimalCopy.insert(0, '-')

        temp: AlternativeBaseFloat = AlternativeBaseFloat(decimalCopy, self.base, self.base) if '-' not in self.decimal else AlternativeBaseFloat(self.decimal[1:], self.base, self.base)
        temp.ancestorDecimal = self.decimal

        return temp
    
    def __abs__(self) -> 'AlternativeBaseFloat':
        temp: AlternativeBaseFloat = AlternativeBaseFloat(self.decimal[1:], self.base, self.base) if self.decimal[0] == '-' else AlternativeBaseFloat(self.decimal, self.base, self.base)

        temp.ancestorDecimal = self.decimal

        return temp
 
    def __pos__(self) -> 'AlternativeBaseFloat':
        return self.converted(self.base)



    def __gt__(self, other) -> bool:

        if isinstance(other, AlternativeBaseFloat):
            return self.dec() > other.dec()
        
        elif isinstance(other, (float, int)):
            return self.dec() > other
        
        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
        
    def __ge__(self, other) -> bool:

        if isinstance(other, (AlternativeBaseFloat, int, float)):
            return (self > other or self == other)
        
        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
        
    def __lt__(self, other) -> bool:

        if isinstance(other, AlternativeBaseFloat):
            return self.dec() < other.dec()
        
        elif isinstance(other, (float, int)):
            return self.dec() < other
        
        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
        
    def __le__(self, other) -> bool:

        if isinstance(other, (AlternativeBaseFloat, int, float)):
            return (self < other or self == other)
        
        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
        
    def __eq__(self, other) -> bool:

        if isinstance(other, AlternativeBaseFloat):

            mutualBase: int = math.lcm(self.base, other.base)
            return self.converted(mutualBase).decimal == other.converted(mutualBase).decimal
        
        elif isinstance(other, (float, int)):
            mutualBase: int = math.lcm(self.base, 10)
            otherObj: AlternativeBaseFloat = AlternativeBaseFloat(float(other), mutualBase)
            return self.converted(mutualBase).decimal == otherObj.decimal
        
        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')
    
    def __ne__(self, other) -> bool:    

        if isinstance(other, (AlternativeBaseFloat, int, float)):  
            return not (self == other)
        
        else:
            raise ValueError('Values must be of type int, float or AlternativeBaseFloat for this operation')



