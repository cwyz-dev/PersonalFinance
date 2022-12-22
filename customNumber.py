from math import ceil, floor, trunc
from decimal import Decimal

stringZero = "0"
stringEmpty = ""
stringSpace = " "
stringDecimal = "."
stringPositive = "+"
stringNegative = "-"
stringScientificPython = "e"

standardDigits = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W",
                  "X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","`","~","!","@",
                  "#","$","%","^","&","*","(",")","-","_","=","+","[","{","]","}","|",";",":",",","<",">","/","?"]
baseNames = ["nullary", "unary", "binary", "trinary", "quaternary", "quinary", "seximal", "septimal", "octal", "nonary", "decimal", "elevenary",
             "dozenal", "baker's dozenal", "biseptimal", "triquinary", "hex", "suboptimal", "triseximal", "untriseximal", "vigesimal", "triseptimal",
             "bielevenary", "unbielevenary", "tetraseximal", "pentaquinary", "biker's dozenal", "trinonary", "tetraseptimal", "untetraseptimal",
             "pentaseximal", "unpentaseximal", "tetroctal", "trielevenary", "bisuboptimal", "pentaseptimal", "niftimal", "unniftimal", "bintriseximal",
             "triker's dozenal", "pentoctal", "pentagesimal", "trisuboptimal", "tetraker's dozenal", "untetraker's dozenal", "hexanonary",
             "pentelevenary", "heptoctal", "trintriseximal", "bintetraseptimal", "unbintetraseptimal", "hexagesimal", "unhexagesimal",
             "binpentaseximal", "heptanonary", "octoctal", "pentaker's dozenal", "hexelevenary", "unhexelevenary", "tetrasuboptimal", "trinbielevenary",
             "heptagesimal", "unheptagesimal", "octononary", "unoctononary", "binniftimal", "pentatriquinary", "tetruntriseximal", "heptelevenary",
             "hexaker's dozenal", "unhexaker's donzenal", "octogesimal", "ennanonary", "binpentoctal", "unbinpentoctal", "heptadozenal",
             "pentasuboptimal", "binhexaseptimal", "trintetraseptimal", "octoelevenary", "unoctelevenary", "ennagesimal"]

class customNumber:
    def convertBaseTenWholeValueToDigits(self, value, digits):
        if not(isinstance(value, int)):
            value = int(value)
        out = stringEmpty
        remainder = value
        length = len(digits)
        while remainder > 0:
            x = remainder  % length
            remainder = floor(remainder / length)
            out += str(digits[x])
        out += str(digits[0])
        while (len(out) > 1 and out[-1] == stringZero):
            out = out[:-1]
        out = out[::-1]
        return out

    def findRepetitionPoint(self, value):
        replacementCharacter = "`"
        value = str(value)
        if len(value) > 1:
            for i, _ in enumerate(value):
                for j, _ in enumerate(value[i + 1:]):
                    tempString = value[i:i + j]
                    tempValue = value.replace(tempString, replacementCharacter)
                    valid = True
                    #if (tempValue[-1] != replacementCharacter and (self.digits.index(tempValue[-1]) == (self.digits.index(tempString[-1]) + 1))
                    #    and self.digits.index(tempString[-1]) >= (len(self.digits) / 2)):
                    #    tempValue = tempValue[:-1]
                    for digit in tempValue[tempValue.find(replacementCharacter):]:
                        if digit != replacementCharacter:
                            valid = False
                    if valid and len(tempValue) > 1:
                        while (i > 0 and value[i - 1] == tempString[-1]):
                            i -= 1
                            tempString = value[i:i + j]
                        return (i, i + j)
        return (-1, len(value))

    def convertBaseTenFractionValueToDigits(self, value, digits):
        remainder = float(f"0.{str(value)}")
        out = stringEmpty
        while remainder > 0:
            x = remainder * len(digits)
            portions = str(x).split(".")
            if stringScientificPython in str(x):
                tempX = str(x).split(stringScientificPython)
                primary = tempX[1].split(stringNegative)
                if len(primary) > 1:
                    primary = int(primary[1])
                else:
                    primary = int(primary[0])
                portions = [stringZero, f"{0:0<{primary-1}}{tempX[0].replace(stringDecimal,stringEmpty)}"]
            out += str(digits[int(portions[0])])
            if len(portions) == 1 or len(out) > (len(digits) ** 2):
                break
            remainder = float(f"0.{portions[1]}")
        repeatIndecies = self.findRepetitionPoint(out)
        out = out[:repeatIndecies[1]]
        return (out, repeatIndecies[0])

    def convertDigitsValueToBaseTenString(self, value, digits):
        value = str(value)
        rollingSum = stringEmpty
        carry = 0
        for digit in value[::-1]:
            x = str(digits.index(digit) + carry)
            rollingSum += x[-1]
            if len(x) > 1:
                carry = int(x[:-1])
            else:
                carry = 0
        return rollingSum[::-1]

    def extend(self, a, b, right=False):
        maxLength = max(len(a), len(b))
        if right:
            a = f"{a:0<{maxLength}}"
            b = f"{b:0<{maxLength}}"
        else:
            a = f"{a:0>{maxLength}}"
            b = f"{b:0>{maxLength}}"
        return (a, b)

    def stringAdd(self, a, b, right=False):
        a, b = self.extend(a, b, right)
        carry = 0
        out = stringEmpty
        for aDigit, bDigit in zip(a[::-1], b[::-1]):
            val = self.digits.index(aDigit) + self.digits.index(bDigit) + carry
            val = self.convertBaseTenWholeValueToDigits(val, self.digits)
            out += val[-1]
            if len(val) > 1:
                carry = self.digits.index(val[:-1])
            else:
                carry = 0
        return (carry, out[::-1])

    def stringSubtract(self, a, b, right=False):
        a, b = self.extend(a, b, right)
        grab = 0
        out = stringEmpty
        for aDigit, bDigit in zip(a[::-1], b[::-1]):
            if grab:
                if aDigit == self.digits[0]:
                    aDigit = self.digits[-1]
                    grab = 1
                else:
                    aDigit = self.digits[self.digits.index(aDigit) - 1]
                    grab = 0
            if self.digits.index(aDigit) < self.digits.index(bDigit):
                aDigit = self.digits.index(aDigit) + len(self.digits)
                grab += 1
            else:
                aDigit = self.digits.index(aDigit)
            val = self.digits[aDigit - self.digits.index(bDigit)]
            out += val
        return (grab, out[::-1])

    def stringMultiply(self, a, b):
        runningTotal = stringEmpty
        for i, bDigit in enumerate(b[::-1]):
            carry = 0
            val = stringEmpty
            for aDigit in a[::-1]:
                digitCalc = self.convertBaseTenWholeValueToDigits((self.digits.index(aDigit) * self.digits.index(bDigit)) + carry,
                                                                  self.digits)
                if len(digitCalc) > 1:
                    carry = self.digits.index(digitCalc[0])
                    val += digitCalc[1]
                else:
                    val += digitCalc
                    carry = 0
            if carry != 0:
                val += self.digits[carry]
            val = f"{val:0>{len(val)+i}}"[::-1]
            x, runningTotal = self.stringAdd(runningTotal, val)
            if x:
                runningTotal = f"{str(self.digits[x])}{runningTotal}"
        return runningTotal

    def getFactors(self, value):
        value = int(value)
        return set(x for tup in ([i, value//i] 
                for i in range(1, int(value**0.5)+1) if value % i == 0) for x in tup)

    def fractionReduce(self, numerator, denominator):
        numerator = int(numerator)
        denominator = int(denominator)
        commonFactors = list(self.getFactors(numerator).intersection(self.getFactors(denominator)))
        if len(commonFactors) > 1:
            return (numerator / commonFactors[-1], denominator / commonFactors[-1])
        else:
            return (numerator, denominator)

    def listEquality(self, aList, bList):
        if len(aList) != len(bList): return False
        for a, b in zip(aList, bList):
            if a != b:
                return False
        return True
    
    # DUnders   
    def __init__(self, incoming, digits, scientificSymbol, repetition=-1):
        #def decimalConversion(decimalString, digits):
        #    powerRaise = (len(digits) ** 2) # This number needs tuning...
        #    temp = self.convertBaseTenValueToDigits(float(decimalString) * (len(digits) ** powerRaise), digits)
        #    return (temp[:len(temp) - powerRaise], temp[len(temp) - powerRaise:])
            
        self.negative = False
        self.scientific = scientificSymbol
        self.whole = stringZero
        self.fraction = stringZero
        self.repetition = repetition
        self.digits = standardDigits[:10]

        if isinstance(digits, int):
            digits = standardDigits[:digits]
        elif isinstance(digits, list):
            digits = digits
        elif isinstance(digits, str):
            if digits in baseNames:
                digits = standardDigits[:baseNames.index(digits.lower())]
            else:
                print(f"Unsupported base name: {digits}")
        else:
            print(f"Unsupported base: {digits} of type {type(digits)}")

        if isinstance(incoming, customNumber):
            self.overwrite(incoming)
        elif isinstance(incoming, list):
            # Assume only giving values in the digitList
            if len(incoming) == 3:
                if incoming[0] != stringEmpty:
                    self.negative = incoming[0]
                if incoming[1] != stringEmpty:
                    self.whole = str(incoming[1])
                if incoming[2] != stringEmpty:
                    self.fraction = str(incoming[2])
                self.digits = digits
            elif len(incoming) == 1:
                self.overwrite(customNumber(incoming[0], self.digits, self.scientific))
            else:
                print(f"Unsuported list setup: {incoming}. Valid list is '[sign, whole, decimal]'")
        elif isinstance(incoming, int) or isinstance(incoming, float):
            if incoming != 0:
                if (incoming/abs(incoming)) < 0:
                    self.negative = True
            if isinstance(incoming, int):
                self.whole = str(abs(incoming))
            elif isinstance(incoming, float):
                portions = str(abs(incoming)).split(stringDecimal)
                self.whole = str(portions[0])
                self.fraction = str(portions[1])
            if not(self.listEquality(standardDigits[:10], digits)):
                self.overwrite(self.convert(digits, self.scientific))
        elif isinstance(incoming, str): # Only takes strings for fractional representations, assumes base 10 inputs
            if len(incoming) > 0:
                power = stringZero
                incoming = incoming.replace(stringSpace, stringEmpty)
                if self.scientific in incoming:
                    segments = incoming.split(self.scientific)
                    power = segments[1]
                    incoming = segments[0]
                if incoming[0] in [stringNegative, stringPositive]:
                    self.negative = (incoming[0] == stringNegative)
                    incoming = incoming[1:]
                portions = incoming.split(stringDecimal)
                if len(portions) == 1:
                    portions = [portions[0], stringZero]
                if portions[0] == stringEmpty:
                    portions[0] = stringZero
                self.whole = portions[0]
                if self.whole[0] == stringNegative:
                    self.whole = self.whole[1:]
                self.fraction = portions[1]
                if power != stringZero:
                    power = customNumber(power, self.digits, self.scientific)
                    power = int(power)
                    temp = f"{self.whole}{self.fraction}"
                    if power > 0:
                        temp = f"{temp}{stringEmpty:{stringZero}<{power + 1}}"
                    else:
                        temp = f"{stringEmpty:{stringZero}<{abs(power)}}{temp}"
                    self.whole = temp[:len(temp) - len(self.fraction) - 1]
                    self.fraction = temp[len(temp) - len(self.fraction) - 1:]
                if not(self.listEquality(standardDigits[:10], digits)):
                    self.overwrite(self.convert(digits, self.scientific))
        else:
            print(f"Unsupported value: {incoming} of type {type(incoming)}")
        self.cleanUp()

    def __int__(self):
        rollingSum = 0
        for i, digit in enumerate(self.whole[::-1]):
            rollingSum += (self.digits.index(digit)) * (len(self.digits) ** i)
        if self.negative:
            rollingSum *= -1
        if rollingSum < 0:
            rollingSum = ceil(rollingSum)
        else:
            rollingSum = floor(rollingSum)
        return rollingSum

    def __str__(self):
        out = f"+{self.whole}{stringDecimal}"
        
        if self.repetition != -1:
            out = f"{out}{self.fraction[:self.repetition]}[{self.fraction[self.repetition:]}]"
        else:
            out = f"{out}{self.fraction}"
        
        if self.negative:
            out = f"-{out[1:]}"
            
        if len(self.digits) <= len(baseNames):
            custom = stringEmpty
            for curDigit, baseDigit in zip(self.digits, standardDigits):
                if curDigit != baseDigit:
                    custom = "custom "
                    break
            out = f"{out} ({custom}{baseNames[len(self.digits)]})"
        else:
            out = f"{out} (base {len(self.digits)} (decimal))"
            
        return out

    def __repr__(self):
        return str(self)

    def __float__(self):
        rollingSum = 0.0
        for i, digit in enumerate(self.whole[::-1]):
            rollingSum += (self.digits.index(digit)) * (len(self.digits) ** i)
        for i, digit in enumerate(self.fraction):
            rollingSum += (self.digits.index(digit)) / (len(self.digits) ** (i + 1))
        if self.repetition != -1:
            x = len(self.fraction)
            for i in range(len(self.digits) ** 2):
                for j, digit in enumerate(self.fraction[self.repetition:]):
                    temp = (self.digits.index(digit) / (len(self.digits) ** (x + (len(self.fraction[self.repetition:]) * i) + j + 1)))
                    tempRoll = rollingSum + temp
                    if (tempRoll - rollingSum) > 0.0:
                        rollingSum = tempRoll
        if self.negative:
            rollingSum *= -1
        return rollingSum

    def __abs__(self):
        return customNumber([False, self.whole, self.fraction], self.digits, self.scientific)

    def __round__(self, n):
        temp = self.duplicate()
        if temp.repetition != -1:
            originalFraction = temp.fraction
            for i in range(ceil(n / len(temp.fraction))):
                temp.fraction += originalFraction
        if len(temp.fraction) > n:
            if temp.digits.index(temp.fraction[n]) < floor(len(temp.digits)):
                temp.decimal = temp.decimal[:n]
            else:
                oString = stringEmpty
                add = True
                temp.decimal = temp.decimal[:n+1]
                for digit in temp.decimal[::-1]:
                    integerDigit = temp.digits.index(digit)
                    if add:
                        integerDigit += 1
                        if integerDigit == len(temp.digits):
                            integerDigit = 0
                        else:
                            add = False
                    oString += temp.digits[integerDigit]
                oString = oString[::-1]
                temp.fraction = oString[:-1]
        temp.cleanUp()
        return temp

    def __floor__(self):
        temp = trunc(self)
        if temp.negative:
            temp -= 1
        temp.cleanUp()
        return temp

    def __ceil__(self):
        temp = trunc(self)
        if not(temp.negative):
            temp += 1
        temp.cleanUp()
        return temp

    def __trunc__(self):
        temp = self.duplicate()
        temp.fraction = stringZero
        temp.cleanUp()
        return temp

    def __bool__(self):
        return self == 0

    def __nonzero__(self):
        return self.__bool__()

    def __add__(self, other):        
        temp, other = self.prep(other)
        
        if temp == 0:
            temp.overwrite(other)
        elif other != 0:
            tempAbs = abs(temp)
            otherAbs = abs(other)
            if (temp < 0 and other < 0):
                temp = tempAbs + otherAbs
                temp.negate()
            elif (temp < 0 or other < 0):
                if temp < 0:
                    temp = other - tempAbs
                else:
                    temp -= otherAbs
            else:
                x, temp.fraction = self.stringAdd(temp.fraction, other.fraction, True)
                _, temp.whole = self.stringAdd(temp.whole, self.digits[x])
                x, temp.whole = self.stringAdd(temp.whole, other.whole)
                while x != 0:
                    x, temp.whole = self.stringAdd(temp.whole, f"{x:0<{len(temp.whole) + 1}}")
        temp.cleanUp()
        return temp

    def __sub__(self, other):
        temp, other = self.prep(other)
        if temp == 0:
            temp.overwrite(other)
            temp.negate()
        elif other != 0:
            tempAbs = abs(temp)
            otherAbs = abs(temp)
            if (temp < 0 and other < 0):
                temp = tempAbs - otherAbs
                temp.negate()
            elif (temp < 0 or other < 0):
                if temp <0:
                    temp = tempAbs + otherAbs
                    temp.negate()
                else:
                    temp += otherAbs
            else:
                if temp == other:
                    temp = customNumber(0, self.digits, self.scientific)
                elif temp < other:
                    temp = other - temp
                    temp.negate()
                else:
                    x, temp.fraction = self.stringSubtract(temp.fraction, other.fraction, True)
                    if x:
                        _, temp.whole = self.stringSubtract(temp.whole, str(x))
                    _, temp.whole = self.stringSubtract(temp.whole, other.whole)
        temp.cleanUp()
        return temp

    def __mul__(self, other):
        temp, other = self.prep(other)

        if temp == 0 or other == 0:
            temp.overwrite(0)
        elif abs(temp) == 1:
            temp.overwrite(other)
            if temp == -1:
                temp.negate()
        elif other == -1:
            temp.negate()
        elif other != 1:
            tempAbs = abs(temp)
            otherAbs = abs(other)
            
            if otherAbs < len(standardDigits):
                if int(otherAbs) == len(self.digits):
                    tempAbs.whole = f"{tempAbs.whole}{tempAbs.fraction[0]}"
                    tempAbs.fraction = f"{tempAbs.fraction[1:]}"
                    tempAbs.cleanUp()
                    otherAbs /= int(otherAbs)
                else:
                    newBase = customNumber(1, int(otherAbs), temp.scientific)
                    tempConv = tempAbs.convert(newBase.digits, newBase.scientific)
                    tempConv.whole = f"{tempConv.whole}{tempConv.fraction[0]}"
                    tempConv.fraction = f"{tempConv.fraction[1:]}"
                    tempConv.cleanUp()
                    tempAbs.overwrite(tempConv.convert(temp.digits, temp.scientific))
                    otherAbs /= int(otherAbs)
            else:
                factors = self.factorsOfWhole(otherAbs)
                for factor in factors:
                    tempAbs *= factor
                    otherAbs /= factor
            
            maxDecimalLength = max(len(tempAbs.fraction), len(otherAbs.fraction))
            newDecimalLength = 2 * maxDecimalLength
            tempAbs.fraction = f"{tempAbs.fraction:0<{maxDecimalLength}}"
            otherAbs.fraction = f"{otherAbs.fraction:0<{maxDecimalLength}}"
            val = self.stringMultiply(f"{tempAbs.whole}{tempAbs.fraction}", f"{otherAbs.whole}{otherAbs.fraction}")
            temp.overwrite(customNumber([((self < 0 or other < 0) and not(self < 0 and other < 0)),
                                         val[:len(val) - newDecimalLength], val[len(val) - newDecimalLength:]], self.digits,
                                        self.scientific))
        temp.cleanUp()
        return temp

    def division(self, other, wholePortionOnly=False):
        temp, other = self.prep(other)
        tempAbs = abs(temp)
        otherAbs = abs(other)
        
        if temp == other:
            temp.overwrite(1)
        elif not(temp == 0 or other == 0 or other == 1):
            if otherAbs < len(standardDigits):
                if int(otherAbs) == len(self.digits):
                    tempAbs.fraction = f"{tempAbs.whole[-1]}{tempAbs.fraction}"
                    tempAbs.whole = f"{tempAbs.whole[:-1]}"
                    tempAbs.cleanUp()
                    otherAbs /= int(otherAbs)
                else:
                    newBase = customNumber(1, int(otherAbs), temp.scientific)
                    tempConv = tempAbs.convert(newBase.digits, newBase.scientific)
                    tempConv.fraction = f"{tempConv.whole[-1]}{tempConv.fraction}"
                    tempConv.whole = f"{tempConv.whole[:-1]}"
                    tempConv.cleanUp()
                    tempAbs.overwrite(tempConv.convert(tempAbs.digits, tempAbs.scientific))
                    otherAbs /= int(otherAbs)
            else:
                factors = self.factorsOfWhole(otherAbs)
                for factor in factors:
                    tempAbs /= factor
                    otherAbs /= factor
            
            if wholePortionOnly:
                tempAbs.fraction = stringZero
            elif not(otherAbs == 0 or otherAbs == 1):
                out = stringEmpty
                totalPrecision = (len(tempAbs.whole) + len(tempAbs.fraction) + len(otherAbs.whole) + len(otherAbs.fraction)) * 2
                dividend = f"{tempAbs.whole}{tempAbs.fraction:0<{totalPrecision - len(tempAbs.whole)}}"
                remainder = customNumber(dividend[0], self.digits, self.scientific)
                i = 1
                while ((remainder > 0 or i < len(dividend)) and i < (len(self.digits) ** 2)):
                    j = 0
                    while remainder >= otherAbs:
                        j += 1
                        remainder -= otherAbs
                    out += self.digits[j]
                    remainder *= len(self.digits)
                    remainder += int(dividend[i])
                    i += 1
                tempAbs.overwrite(customNumber([False, out[:len(tempAbs.whole)], out[len(tempAbs.whole):]], self.digits, self.scientific))
            temp.overwrite(tempAbs)

        if (((temp < 0) or (other < 0)) and not((temp < 0) and (other < 0))):
            temp.negate()
        
        temp.cleanUp()
        return temp

    def __floordiv__(self, other):
        return float(self.division(other, True))

    def __truediv__(self, other):
        return self.division(other, False)

    def __div__(self, other):
        return self.division(other, False)

    def __mod__(self, other):
        temp, other = self.prep(other)
        if temp == other:
            return customNumber(0, self.digits, self.scientific)
        elif temp < other:
            return temp
        else:
            temp = abs(temp - (other * self.division(other, True)))
            temp.cleanUp()
            return temp

    def __pow__(self, other):
        temp, other = self.prep(other)

        if other == 0:
            temp.overwrite(customNumber(1, temp.digits, temp.scientific))
        elif not(temp == 1 or other == 1):
            whole = customNumber(1, temp.digits, temp.scientific)
            # Whole portion (basic powers)
            if other.whole != self.digits[0]:
                whole = tempAbs.duplicate()
                if whole == len(temp.digits):
                    whole.whole = f"{temp.digits[1]}{'':{temp.digits[0]}<{int(other)}}"
                    whole.fraction = stringEmpty
                else:
                    binary = other.duplicate()
                    if len(other.digits) != 2:
                        binaryOne = customBinary(1)
                        binary = other.convert(binaryOne.digits, binaryOne.scientific)
                    for binaryDigit in binary.whole[1:]:
                        whole *= whole
                        if binaryDigit == binary.digits[1]:
                            whole *= abs(temp)
                whole.findRepetition()
            # Decimal portion (fractional powers)
            fractional = customNumber(1, temp.digits, temp.scientific)
            if other.fraction != self.digits[0]:
                n, d = self.fractionReduce(other.fraction, 10 ** len(other.fraction))
                fractional = tempAbs.root(d)
                fractional **= n
                fractional.findRepetition()
            temp.overwrite(whole * fractional)
        temp.cleanUp()
        return temp

    def __lt__(self, other):
        temp, other = self.prep(other)

        if temp.negative and not(other.negative):
            return True
        elif other.negative and not(temp.negative):
            return False

        maxWholeLength = max(len(temp.whole), len(other.whole)) ** 2
        for tempDigit, otherDigit in zip(f"{temp.whole:0>{maxWholeLength}}", f"{other.whole:0>{maxWholeLength}}"):
            if tempDigit != otherDigit:
               return temp.digits.index(tempDigit) < self.digits.index(otherDigit)
        maxFractionLength = max(len(temp.fraction), len(other.fraction))
        for tempDigit, otherDigit in zip(f"{temp.fraction:0<{maxFractionLength}}", f"{other.fraction:0<{maxFractionLength}}"):
            if tempDigit != otherDigit:
                return temp.digits.index(tempDigit) < temp.digits.index(otherDigit)
        return False

    def __le__(self, other):
        return ((self == other) or (self < other))

    def __eq__(self, other):
        if self.negative != (other < 0): return False
        if isinstance(other, int) and self.fraction != stringZero: return False

        if len(self.digits) == 10:
            decimal = True
            for curDigit, newDigit in zip(self.digits, standardDigits[:len(self.digits)]):
                if curDigit != newDigit:
                    decimal = False
                    break
        
            if decimal:
                if isinstance(other, int):
                    return (self.whole == str(abs(other)))
                elif isinstance(other, float) or isinstance(other, Decimal):
                    portions = str(abs(other)).split(stringDecimal)
                    return ((self.whole == portions[0]) and (self.fraction == portions[1]))
                #elif isinstance(other, str):
                
        temp, other = self.prep(other)
        return ((temp.whole == other.whole) and (temp.fraction == other.fraction))

    def __gt__(self, other):
        temp, other = self.prep(other)

        if other.negative and not(temp.negative):
            return True
        elif temp.negative and not(other.negative):
            return False

        maxWholeLength = max(len(temp.whole), len(other.whole))
        for tempDigit, otherDigit in zip(f"{temp.whole:0>{maxWholeLength}}", f"{other.whole:0>{maxWholeLength}}"):
            if tempDigit != otherDigit:
                return temp.digits.index(tempDigit) > temp.digits.index(otherDigit)
        maxFractionLength = max(len(temp.fraction), len(other.fraction))
        for tempDigit, otherDigit in zip(f"{temp.fraction:0<{maxFractionLength}}", f"{other.fraction:0<{maxFractionLength}}"):
            if tempDigit != otherDigit:
                return temp.digits.index(tempDigit) > temp.digits.index(otherDigit)
        return False

    def __ge__(self, other):
        return ((self == other) or (self > other))

    def __hash__(self):
        return hash((self.negative, self.whole, self.fraction, self.repetition, tuple(self.digits), self.scientific))

    def root(self, other):
        temp, other = self.prep(other)
        tempAbs = abs(temp)
        otherAbs = abs(other)
        customOne = customNumber(1, self.digits, self.scientific)
        if not(temp == 1 or temp < 0 or other == 0 or otherAbs == 1):
            tolerance = customNumber(10, self.digits, self.scientific)
            tolerancePrecision = max(len(temp.fraction), len(other.fraction), len(self.digits))
            tolerance **= tolerancePrecision
            tolerance = customOne / tolerance
            x = tempAbs.duplicate()
            root = (tempAbs * 1.1) / otherAbs
            otherMinusOne = otherAbs - 1
            i = 0
            while ((abs(x - root) > tolerance) and (i < tolerancePrecision ** 2)):
                x.overwrite(root)
                root = tempAbs.duplicate()
                x.cleanUp()
                root = ((x * otherMinusOne) + (tempAbs / (x ** otherMinusOne))) / otherAbs
                i += 1
            temp.overwrite(x)
        if other < 0:
            temp = customOne / temp
        temp.cleanUp()
        return temp

    def findRepetition(self):
        if self.repetition == -1:
            repeatIndecies = self.findRepetitionPoint(self.fraction)
            self.fraction = self.fraction[:repeatIndecies[1]]
            self.repetition = repeatIndecies[0]

    def fillZeroes(self):
        if len(self.whole) == 0:
            self.whole = stringZero
        if len(self.fraction) == 0:
            self.fraction = stringZero

    def removeWholeLeadingZeroes(self):
        while (len(self.whole) > 1 and self.whole[0] == stringZero):
            self.whole = self.whole[1:]

    def removeFractionTrailingZeroes(self):
        while (len(self.fraction) > 1 and self.fraction[-1] == stringZero):
            self.fraction = self.fraction[:-1]

    def checkZero(self):
        if (self.whole == stringZero and self.fraction == stringZero):
            self.negative = False

    def cleanUp(self):
        self.fillZeroes()
        self.removeWholeLeadingZeroes()
        self.removeFractionTrailingZeroes()
        self.findRepetition()
        self.checkZero()

    def duplicate(self):
        return customNumber([self.negative, self.whole, self.fraction], self.digits, self.scientific, self.repetition)

    def convert(self, digitList, scientificSymbol):
        if isinstance(digitList, str):
            if digitList in baseNames:
                digitList = standardDigits[:baseNames.index(digitList.lower())]
            else:
                print(f"Unsupported base name: {digitList}, defaulting to decimal")
                digitList = standardDigits[:baseNames.index("decimal")]
        elif isinstance(digitList, int):
            digitList = standardDigits[:digitList]
                
        if abs(self) == len(digitList):
            return customNumber([self.negative, f"{digitList[1]}{digitList[0]}", f"{digitList[0]}"], digitList, scientificSymbol)
        elif len(self.digits) == len(digitList):
            mappings = dict({})
            for curDigit, newDigit in zip(self.digits, digitList):
                if curDigit != newDigit:
                    mappings[curDigit] = newDigit
            tempWhole = self.whole
            tempFraction = self.fraction
            for curDigit in mappings.keys():
                tempWhole = tempWhole.replace(curDigit, mappings[curDigit])
                tempFraction = tempFraction.replace(curDigit, mappings[curDigit])
            return customNumber([self.negative, tempWhole, tempFraction], digitList, scientificSymbol)
        else:
            divisor = customNumber(len(digitList), self.digits, self.scientific)
            # Whole portion
            out = stringEmpty
            temp = f"{self.whole}"
            while temp != stringZero:
                carry = stringZero
                nextNumber = stringEmpty
                for digit in temp:
                    val = customNumber([False, digit, stringZero], self.digits, self.scientific) + (carry * len(self.digits))
                    i = 0
                    while val >= divisor:
                        val -= divisor
                        i += 1
                    nextNumber += self.digits[i]
                    carry = val
                temp = stringZero
                for i, digit in enumerate(nextNumber):
                    if digit != stringZero:
                        temp = nextNumber[i:]
                        break
                out += digitList[int(carry)]
            out = out[::-1]
            wholeLength = len(out)
            
            # Fraction portion
            divisor = len(self.digits) ** len(self.fraction)
            remainder = float(f"{self.fraction}") / divisor
            while remainder > 0:
                x = remainder * len(digitList)
                portions = str(x).split(".")
                if stringScientificPython in str(x):
                    tempX = str(x).split(stringScientificPython)
                    primary = tempX[1].split(stringNegative)
                    if len(primary) > 1:
                        primary = int(primary[1])
                    else:
                        primary = int(primary[0])
                    portions = [stringZero, f"{0:0<{primary-1}}{tempX[0].replace(stringDecimal, stringEmpty)}"]
                if len(portions[0]) > 1:
                    portions[1] = f"{portions[0][1:]}{portions[1]}"
                    portions[0] = portions[0][0]
                out += str(digitList[int(portions[0])])
                if len(portions) == 1 or len(out) > (len(digitList) ** 2):
                    break
                remainder = float(f"{portions[1]}") / divisor
            
            return customNumber([self.negative, out[:wholeLength], out[wholeLength:]], digitList, scientificSymbol)

    def overwrite(self, other):
        if not(isinstance(other, customNumber)):
            other = customNumber(other, self.digits, self.scientific)
        self.negative = other.negative
        self.whole = other.whole
        self.fraction = other.fraction
        self.digits = other.digits
        self.scientific = other.scientific
        self.repetition = other.repetition
        self.cleanUp()

    def negate(self):
        self.negative = not(self.negative)

    def prep(self, other):
        if not(isinstance(other, customNumber)):
            other = customNumber(other, self.digits, self.scientific)
        elif not(self.digits == other.digits and self.scientific == other.scientific):
            other = other.convert(self.digits, self.scientific)
        other.cleanUp()
        if other.repetition != -1:
            newFraction = other.fraction
            for i in range(floor((len(other.digits) * 5)/len(other.fraction[other.repetition:]))):
                for j, digit in enumerate(other.fraction[other.repetition:]):
                    newFraction += digit
            other.fraction = newFraction
            other.repetition = -1
        
        temp = self.duplicate()
        temp.cleanUp()
        if temp.repetition != -1:
            newFraction = temp.fraction
            for i in range(floor((len(temp.digits) * 5)/len(temp.fraction[temp.repetition:]))):
                for j, digit in enumerate(temp.fraction[temp.repetition:]):
                    newFraction += digit
            temp.fraction = newFraction
            temp.repetition = -1
        return (temp, other)

    def factorsOfWhole(self, other):
        temp, other = self.prep(other)
        other = int(trunc(other))
        p = 2
        factors = []
        while other >= (p ** 2):
            if (other % p) == 0:
                factors.append(p)
                other /= p
                p = 2
            else:
                p += 1
        factors.append(int(other))
        return factors

# Some typical bases
class customBinary(customNumber):
    def __init__(self, incoming):
        super().__init__(incoming, "binary", stringScientificPython)

class customOctal(customNumber):
    def __init__(self, incoming):
        super().__init__(incoming, "octal", stringScientificPython)

class customDecimal(customNumber):
    def __init__(self, incoming):
        super().__init__(incoming, "decimal", stringScientificPython)

class customHex(customNumber):
    def __init__(self, incoming):
        super().__init__(incoming, "hex", stringScientificPython)

# Basic versions of polar complex numbers
class customComplexNumber():
    def __init__(self, incomingR, incomingTheta, digits, scientific):
        self.magnitude = customNumber(incomingR, digits, scientific)
        self.phase = customNumber(incomingTheta, digits, scientific)

    def __str__(self):
        outMagnitude = f"+{self.magnitude.whole}{stringDecimal}"
        if self.magnitude.repetition != -1:
            outMagnitude = f"{outMagnitude}{self.magnitude.fraction[:self.magnitude.repetition]}[{self.magnitude.fraction[self.magnitude.repetition:]}]"
        else:
            outMagnitude = f"{outMagnitude}{self.magnitude.fraction}"
        if self.magnitude.negative:
            outMagnitude = f"-{outMagnitude[1:]}"

        outPhase = f"+{self.phase.whole}{stringDecimal}"
        if self.phase.repetition != -1:
            outPhase = f"{outPhase}{self.phase.fraction[:self.phase.repetition]}[{self.phase.fraction[self.phase.repetition:]}]"
        else:
            outPhase = f"{outPhase}{self.phase.fraction}"
        if self.magnitude.negative:
            outPhase = f"-{outPhase[1:]}"
        
        out = f"{outMagnitude} * e^(i * {outPhase})"

        if len(self.magnitude.digits) <= len(baseNames):
            out = f"{out} ({baseNames[len(self.magnitude.digits)]})"
        else:
            out = f"{out} (base {len(self.magnitude.digits)} (decimal))"
        
        return out

class customComplexBinary(customComplexNumber):
    def __init__(self, incomingR, incomingTheta):
        super().__init__(incomingR, incomingTheta, "binary", stringScientificPython)

class customComplexDecimal(customComplexNumber):
    def __init__(self, incomingR, incomingTheta):
        super().__init__(incomingR, incomingTheta, "decimal", stringScientificPython)

if __name__ == "__main__":
    x = customBinary(2)
    print(f"{x} | {int(x)} | {float(x)}")
    x *= 10
    print(f"{x} | {int(x)} | {float(x)}")
