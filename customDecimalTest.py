from    time            import  perf_counter     as  pc

from    customNumber   import  customDecimal, customBinary, customOctal, customHex
from    decimal     import  Decimal
import sys

def testRoot(a, b, requiredOutput, precision):
    start = pc()
    x = customDecimal(a)
    w = x.duplicate()
    y = customDecimal(b)
    x = x.root(y)
    z = x.duplicate()
    z **= y
    w -= z
    w = abs(w)
    end = pc()
    xStr = str(a)
    if isinstance(a, str):
        xStr = f"'{a}'"
    yStr = str(b)
    if isinstance(b, str):
        yStr = f"'{b}'"
    inputStr = f"{yStr} root of {xStr}:"
    if not(abs(requiredOutput - x) < precision):
        print(f"\t\t{end-start:22} s\t{inputStr:20}\t{x}\tshould be {requiredOutput}")
        #print(f"\t\t{'':{'-'}<30}\n\t\t{end-start:22} s\t{inputStr:20}\t{x}\n\t\t\t\t\t\tProof:\t\t\t{z}\n\t\t\t\t\t\tError:\t\t\t{w}")

roots = dict({
    1: dict({
        1: 1,
        2: 1,
        3: 1,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 1,
        10: 1}),
    2: dict({
        1: 2,
        2: 1.4142135624,
        3: 1.2599210499,
        4: 1.189207115,
        5: 1.148698355,
        6: 1.1224620483,
        7: 1.1040895137,
        8: 1.0905077327,
        9: 1.0800597389,
        10: 1.0717734625}),
    3: dict({
        1: 3,
        2: 1.7320508076,
        3: 1.4422495703,
        4: 1.316074013,
        })})
        
def testRoots():
    print("Root Finding Cases")
    start = pc()
    count = 0
    precision = customDecimal(1) / 10000000000
    for i in range(1, 11):
        print(f"\tRoot Cases for {i}")
        innerStart = pc()
        for j in range(1, 11):
            testRoot(i, j, customDecimal(roots[i][j]), precision)
            count += 1
        innerEnd = pc()
        innerTotalTime = innerEnd - innerStart
        print(f"\tTotal time for roots of {i}: {innerTotalTime} s\tAveraging {(innerTotalTime / len(roots[i].keys()))} s/op over {len(roots[i].keys())} ops\n{'':{'-'}<30}")
    #totalCount = addZeroCount + addOneToNineCount + addTenToNinetyCount
    end = pc()
    totalTime = end - start
    print(f"Total time for root finding: {totalTime} s\tAveraging {(totalTime / count)} s/op over {count} ops\n{'':{'-'}<30}")

def conversion(targetType, value):
    if isinstance(value, type(targetType)):
        return value
    elif isinstance(targetType, int):
        return int(value)
    elif isinstance(targetType, float):
        return float(value)
    elif isinstance(targetType, Decimal):
        return Decimal(value)
    elif isinstance(targetType, customDecimal):
        return customDecimal(value)
    elif isinstance(targetType, customBinary):
        return customBinary(value)
    elif isinstance(targetType, customOctal):
        return customOctal(value)
    elif isinstance(targetType, customHex):
        return customHex(value)
    print(f"No conversion for {type(targetType)} implemented...")
    return value

def testParsing(testType, verbose, maxError):
    def testParse(val, requiredOutput):
        start = pc()
        x = conversion(testType, val)
        end = pc()
        if (requiredOutput != x or verbose):
            error = abs(requiredOutput - x)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStr = str(val)
                if isinstance(val, str):
                    valStr = f"'{valStr}'"
                inputStr = f"{type(testType)}({valStr}):"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{x}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")
            
    outputs = dict({"zero": "0", "positiveOne": "1", "negativeOne": "-1", "positiveTen": "10", "negativeTen": "-10"})
    for o in outputs.keys():
        outputs[o] = conversion(testType, outputs[o])
    
    for c in ["0", 0, 0.0, 0.00, "+0", +0, +0.0, +0.00, "-0", -0, -0.0, -0.00]:
        testParse(c, outputs["zero"])
    for c in ["1", 1, 1.0, 1.00, "+1", +1, +1.0, +1.00]:
        testParse(c, outputs["positiveOne"])
    for c in ["-1", -1, -1.0, -1.00]:
        testParse(c, outputs["negativeOne"])
    for c in ["10", 10, 10.0, 10.00, "+10", +10, +10.0, +10.00]:
        testParse(c, outputs["positiveTen"])
    for c in ["-10", -10, -10.0, -10.00]:
        testParse(c, outputs["negativeTen"])

def testAddition(testType, verbose, maxError):
    def testAdd(valA, valB, requiredOutput):
        start = pc()
        a = conversion(testType, valA)
        b = conversion(testType, valB)
        c = conversion(testType, a + b)
        end = pc()
        if (requiredOutput != c or verbose):
            error = abs(requiredOutput - c)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStrA = str(valA)
                if isinstance(valA, str):
                    valStrA = f"'{valStrA}'"
                valStrB = str(valB)
                if isinstance(valB, str):
                    valStrB = f"'{valStrB}'"
                inputStr = f"{valStrA} + {valStrB}:"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{c}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")

    options = [i for i in range(10, 0, -1)]
    options.extend([i for i in range(100, 0, -10)])
    options.extend([i for i in range(1000, 0, -100)])
    for i, a in enumerate(options):
        for b in options[i:]:
            testAdd(a, b, conversion(testType, a+b))

def testSubtraction(testType, verbose, maxError):
    def testSub(valA, valB, requiredOutput):
        start = pc()
        a = conversion(testType, valA)
        b = conversion(testType, valB)
        c = conversion(testType, a - b)
        end = pc()
        if (requiredOutput != c or verbose):
            error = abs(requiredOutput - c)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStrA = str(valA)
                if isinstance(valA, str):
                    valStrA = f"'{valStrA}'"
                valStrB = str(valB)
                if isinstance(valB, str):
                    valStrB = f"'{valStrB}'"
                inputStr = f"{valStrA} - {valStrB}:"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{c}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")

    options = [i for i in range(10, 0, -1)]
    options.extend([i for i in range(100, 0, -10)])
    options.extend([i for i in range(1000, 0, -100)])
    for i, a in enumerate(options):
        for b in options[i:]:
            testSub(a, b, conversion(testType, a-b))

def testMultiplication(testType, verbose, maxError):
    def testMult(valA, valB, requiredOutput):
        start = pc()
        a = conversion(testType, valA)
        b = conversion(testType, valB)
        c = conversion(testType, a * b)
        end = pc()
        if (requiredOutput != c or verbose):
            error = abs(requiredOutput - c)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStrA = str(valA)
                if isinstance(valA, str):
                    valStrA = f"'{valStrA}'"
                valStrB = str(valB)
                if isinstance(valB, str):
                    valStrB = f"'{valStrB}'"
                inputStr = f"{valStrA} * {valStrB}:"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{c}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")

    options = [i for i in range(10, 0, -1)]
    options.extend([i for i in range(100, 0, -10)])
    options.extend([i for i in range(1000, 0, -100)])
    for i, a in enumerate(options):
        for b in options[i:]:
            testMult(a, b, conversion(testType, a*b))

def testDivision(testType, verbose, maxError):
    def testDiv(valA, valB, requiredOutput):
        start = pc()
        a = conversion(testType, valA)
        b = conversion(testType, valB)
        c = conversion(testType, a / b)
        end = pc()
        if (requiredOutput != c or verbose):
            error = abs(requiredOutput - c)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStrA = str(valA)
                if isinstance(valA, str):
                    valStrA = f"'{valStrA}'"
                valStrB = str(valB)
                if isinstance(valB, str):
                    valStrB = f"'{valStrB}'"
                inputStr = f"{valStrA} / {valStrB}:"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{c}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")

    options = [i for i in range(10, 0, -1)]
    options.extend([i for i in range(100, 0, -10)])
    options.extend([i for i in range(1000, 0, -100)])
    for i, a in enumerate(options):
        for b in options[i:]:
            testDiv(a, b, conversion(testType, a/b))

def testPowers(testType, verbose, maxError):
    def testPower(valA, valB, requiredOutput):
        start = pc()
        a = conversion(testType, valA)
        b = conversion(testType, valB)
        c = conversion(testType, a ** b)
        end = pc()
        if (requiredOutput != c or verbose):
            error = abs(requiredOutput - c)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStrA = str(valA)
                if isinstance(valA, str):
                    valStrA = f"'{valStrA}'"
                valStrB = str(valB)
                if isinstance(valB, str):
                    valStrB = f"'{valStrB}'"
                inputStr = f"{valStrA} ^ {valStrB}:"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{c}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")

    options = [i for i in range(10, 0, -1)]
    #options.extend([i for i in range(100, 0, -10)])
    #options.extend([i for i in range(1000, 0, -100)])
    for i, a in enumerate(options):
        for b in options[i:]:
            testPower(a, b, conversion(testType, a**b))

def testInversion(testType, verbose, maxError):
    def testInverse(val, requiredOutput):
        start = pc()
        x = conversion(testType, val)
        one = conversion(testType, 1)
        y = conversion(testType, one / x)
        end = pc()
        if (requiredOutput != y or verbose):
            error = abs(requiredOutput - y)
            allowedError = conversion(testType, maxError)
            if error > allowedError:
                valStr = str(val)
                if isinstance(val, str):
                    valStr = f"'{valStr}'"
                inputStr = f"{type(testType)}({valStr}):"
                print(f"\t\t{end-start:22} s\t{inputStr:20}\t{y}\tshould be {requiredOutput} (error of {error}) when type is {type(testType)}")
            
    options = [i for i in range(10, 0, -1)]
    options.extend([i for i in range(100, 0, -10)])
    options.extend([i for i in range(1000, 0, -100)])
    for a in options:
        testInverse(a, conversion(testType, 1/a))

def testTypeHarness(testType, verbose=False, maxError="0.00000001"):
    if verbose:
        print(f"TEST CASES for {testType}:")
    start = pc()
    
    testParsing(testType, verbose, maxError)
    testAddition(testType, verbose, maxError)
    testSubtraction(testType, verbose, maxError)
    testMultiplication(testType, verbose, maxError)
    testDivision(testType, verbose, maxError)
    #testPowers(testType, verbose, maxError)
    #testInversion(testType, verbose, maxError)
    #testRoots(testType, verbose, maxError)
    
    end = pc()
    customTime = end - start
    if verbose:
        print(f"Total time for {testType}: {customTime}")
    return customTime

def testHarness(runCount = 1):
    typeSet = (0, 0.0, Decimal(0), customBinary(0), customOctal(0), customHex(0), customDecimal(0))
    timeDict = ({})
    for testType in typeSet:
        timeDict[str(type(testType))] = 0
    start = pc()
    runTime = 0
    for i in range(1, runCount + 1):
        runStart = pc()
        sys.stdout.write('\r')
        sys.stdout.write(f"Run {i:0>{len(str(runCount))}} / {runCount}")
        sys.stdout.flush()
        for testType in typeSet:
            timeDict[str(type(testType))] = ((timeDict[str(type(testType))] * (i-1)) + testTypeHarness(testType, False, "1")) / i
            #sys.stdout.write(f"{type(testType)}, ")
            #sys.stdout.flush()
        runTime = pc() - runStart
    end = pc()

    print(f"\n{'':-<35}\nTotal Time: {end - start} s")
    for testedType in timeDict.keys():
        print(f"{testedType} ran in, on average across {runCount} runs, {timeDict[testedType]} s")
        if testedType != str(type(customDecimal(0))):
            faster = "faster"
            compValue = timeDict[str(type(customDecimal(0)))] / timeDict[testedType]
            if compValue < 1:
                faster = "slower"
                compValue =  timeDict[testedType] / timeDict[str(type(customDecimal(0)))]
            print(f"\t which is {compValue} times {faster} than {str(type(customDecimal(0)))}")
    print(f"{'':-<35}")

if __name__ == "__main__":
    testHarness()
