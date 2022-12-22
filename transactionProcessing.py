from decimal import Decimal as cD
#from customNumber import customDecimal as cD
import datetime as dt
import pandas as pd
import pandas_datareader
import re
import mysql.connector as sql

def loadTransactions(xlsxFileName):
    file = pd.read_excel(xlsxFileName, header=0, keep_default_na=False)
    frame = pd.DataFrame({"":[]})
    file[file["Sort Date"].astype(str).str.strip().astype(bool)]
    frame = file.astype({
        "Sort Date": str, "a": str, "Initial Date": str, "Initial Account": str, "Initial Ticker": str,
        "Initial Quantity": str, "Rate of Initial Asset": str, "b": str, "Final Date": str, "Final Account": str,
        "Final Ticker": str, "Final Quantity": str, "Rate of Final Asset": str, "c": str, "Transaction Fee": str,
        "Transaction Type": str, "Transaction Note": str,
    })
    frame.sort_values([
        "Sort Date", "Initial Date", "Final Date", "Initial Account", "Final Account", "Initial Ticker",
        "Final Ticker", "Initial Quantity", "Final Quantity", "Rate of Initial Asset", "Rate of Final Asset",
        "Transaction Type", "Transaction Fee"
    ])
    return frame

def processTransactions(transactionsFrame, dailySummary, cpis, currentDate, database):
    holdings = dict()
    gains = dict({"total": cD(0), "taxable": cD(0)})
    dailies = dict()

    prevDate = dt.datetime.min
    for i, t in transactionsFrame.iterrows():
        if t[0] == "NaT":
            date = dt.datetime.max
        else:
            date = dt.datetime.strptime(t[0], "%Y-%m-%d %H:%M:%S")
        if date < currentDate:
            prevDate = processTransaction(t, holdings, gains, dailies,
                                          dailySummary, cpis, prevDate,
                                          currentDate, database)
    return (holdings, gains, dailies)

def adjustForInflation(value, cpis, iDate, fDate):
    try:
        return value * (cpis[f"{fDate.year}"][f"{fDate.month:0>2}"] / cpis[f"{iDate.year}"]["{iDate.month:0>2}"])
    except:
        return value

def processTransaction(transaction, holdings, gains, dailies, dailySummary,
                       cpis, prevDate, currentDate, database):
    i, f, e = transaction[2:7], transaction[8:13], transaction[14:]
    if (i[0] == "" and f[0] == ""):
        return prevDate

    iDate, iAccount, iTicker, iQuantity, iRate = i
    fDate, fAccount, fTicker, fQuantity, fRate = f
    fee, action, _, _ = e

    if iDate == "NaT":
        iDate = dt.datetime.max
    else:
        iDate = dt.datetime.strptime(iDate, "%Y-%m-%d %H:%M:%S")
    if fDate == "NaT":
        fDate = dt.datetime.max
    else:
        fDate = dt.datetime.strptime(fDate, "%Y-%m-%d %H:%M:%S")

    if iQuantity != "":
        iQuantity = cD(iQuantity)
        if iQuantity != cD(0):
            iQuantity *= -1
    else:
        iQuantity = cD(0)

    if fee != "":
        fee = cD(fee) * -1
    else:
        fee = cD(0)

    if fQuantity != "":
        fQuantity = cD(fQuantity)
    else:
        fQuantity = cD(0)

    if iTicker == "CAD":
        iRate = cD(1)
        iRateInfl = cD(1)
    else:
        if iRate != "":
            iRate = cD(iRate)
        else:
            if fQuantity != cD(0):
                iRate = abs(cD(iQuantity) / cD(fQuantity))
            else:
                iRate = cD(0)
        iRateInfl = adjustForInflation(iRate, cpis, iDate, currentDate)

    if fTicker == "CAD":
        fRate = cD(1)
        fRateInfl = cD(1)
    else:
        if fRate != "":
            fRate = cD(fRate)
        else:
            if iQuantity != cD(0):
                fRate = abs(cD(fQuantity) / cD(iQuantity))
            else:
                fRate = cD(0)
        fRateInfl = adjustForInflation(fRate, cpis, currentDate, fDate)

    i = iDate, iAccount, iTicker, iQuantity, iRate, iRateInfl
    f = fDate, fAccount, fTicker, fQuantity, fRate, fRateInfl
    e = fee, action

    result = database.callproc("insertTransaction", [i, f, e])

    match action:
        case "Balance":
            modifyAsset(f, holdings)
        case "Payment":
            modifyAsset(f, holdings)
        case "Dividend":
            modifyAsset(f, holdings)
        case "Refund":
            modifyAsset(f, holdings)
        case "Expense":
            typeB(i, e, holdings, gains)
        case "Purchase":
            typeC(i, f, e, holdings, cpis, currentDate)
        case "Split":
            typeD(i, f, e, holdings, gains, cpis, currentDate)
        case "Sale":
            typeE(i, f, e, holdings, gains)
        case "Exchange (Barter)":
            typeE(i, f, e, holdings, gains)
        case "Interest":
            modifyAssetGift(f, holdings)
        case "Gift/ Bonus/ Special Activity":
            modifyAssetGift(f, holdings)
        case "Fee":
            typeG(i, e, holdings, gains)

        case "E-Transfer":
            if iTicker == "":
                modifyAsset(f, holdings)
            elif fTicker == "":
                typeB(i, e, holdings, gains)
        case "Transfer":
            if iTicker == "CAD":
                typeC(i, f, e, holdings, cpis, currentDate)
            else:
                typeD(i, f, e, holdings, gains, cpis, currentDate)

    return min(iDate, fDate)

def typeB(i, e, holdings, gains):
    date, account, ticker, quantity, rate, rateInfl = i
    quantity = quantity + e[0]
    i = date, account, ticker, quantity, rate, rateInfl

    calculateGains(i, holdings, gains)
    modifyAsset(i, holdings)

def typeC(i, f, e, holdings, cpis, currentDate):
    date, account, ticker, quantity, rate, rateInfl = i
    quantity = quantity + e[0]
    i = date, account, ticker, quantity, rate, rateInfl
    
    date, account, ticker, quantity, rate, rateInfl = f
    rate = abs(i[3] / quantity)
    rateInfl = adjustForInflation(rate, cpis, currentDate, date)
    f = date, account, ticker, quantity, rate, rateInfl
    
    modifyAsset(i, holdings)
    modifyAsset(f, holdings)

def typeD(i, f, e, holdings, gains, cpis, currentDate):
    date, account, ticker, quantity, rate, rateInfl = i
    quantity = quantity + e[0]
    rate = getRate(holdings, account, ticker)
    rateInfl = adjustForInflation(rate, cpis, date, currentDate)
    i = date, account, ticker, quantity, rate, rateInfl

    date, account, ticker, quantity, rate, rateInfl = f
    rate = abs((i[3] * i[4]) / quantity)
    rateInfl = abs((i[3] * i[5]) / quantity)
    f = date, account, ticker, quantity, rate, rateInfl
    # Do you get Capital Gains when moving assets between accounts?
    # calculateGains(i, holdings, gains)
    modifyAsset(i, holdings)
    modifyAsset(f, holdings)

def typeE(i, f, e, holdings, gains):
    #print(i,f)
    date, account, ticker, quantity, rate, rateInfl = i
    quantity = quantity + e[0]
    i = date, account, ticker, quantity, rate, rateInfl

    if not(i[4] == 0 and f[4] == 0):
        if i[4] == 0:
            date, account, ticker, quantity, rate, rateInfl = i
            rate = abs((f[3] * f[4]) / quantity)
            rateInfl = abs((f[3] * f[5]) / quantity)
            i = date, account, ticker, quantity, rate, rateInfl
        elif f[4] == 0:
            date, account, ticker, quantity, rate, rateInfl = f
            rate = abs((i[3] * i[4]) / quantity)
            rateInfl = abs((i[3] * i[5]) / quantity)
            f = date, account, ticker, quantity, rate, rateInfl

    calculateGains(i, holdings, gains)
    modifyAsset(i, holdings)
    modifyAsset(f, holdings)

def typeG(i, e, holdings, gains):
    date, account, ticker, quantity, rate, rateInfl = i
    quantity = quantity + e[0]
    i = date, account, ticker, quantity, rate, rateInfl
    calculateGains(i, holdings, gains)
    modifyAssetRateless(i, holdings)

def calculateGains(bundle, holdings, gains):
    date, account, ticker, quantity, rate, rateInfl = bundle
    if account in holdings.keys():
        if ticker in holdings[account].keys():
            if ticker != "CAD":
                curRate = abs(getRate(holdings, account, ticker))
                gain = (abs(quantity) * abs(rate)) - (abs(quantity) * curRate)
                #print(date, account, ticker, gains["total"], gain)
                gains["total"] += gain
                if re.search("RRSP|TFSA", account) == None:
                    gains["taxable"] += gain

def modifyAssetGift(bundle, holdings):
    date, account, ticker, quantity, rate, rateInfl = bundle
    bundle = date, account, ticker, quantity, rate, rateInfl, cD(0), cD(0)
    modifyAsset(bundle, holdings)

def modifyAssetRateless(bundle, holdings):
    date, account, ticker, quantity, _, _ = bundle
    bundle = date, account, ticker, quantity, cD(0), cD(0), cD(0), cD(0)
    modifyAsset(bundle, holdings)

def overMap(bundle):
    if len(bundle) == 6:
        date, account, ticker, quantity, rate, rateInfl = bundle
        return (date, account, ticker, quantity, rate, rateInfl, rate, rateInfl)
    else:
        return bundle

def modifyAsset(bundle, holdings):
    date, account, ticker, quantity, rate, rateInfl, xRate, xRateInfl = overMap(bundle)
    current  = getCurrent(holdings, account, ticker)
    iDate, fDate, cQuantity, cRate, cRateInfl, cXRate, cXRateInfl = current

    if quantity > 0:
        iDate = date
    if quantity < 0:
        fDate = date

    if ticker == "CAD":
        cRate = cD(1)
        cRateInfl = cD(1)
        xRate = cD(1)
        xRateInfl = cD(1)

    if cQuantity == 0:
        cRate = cD(0)
        cRateInfl = cD(0)
        cXRate = cD(0)
        cXRateInfl = cD(0)

    nQuantity = cQuantity + quantity
    if nQuantity != 0:
        nRate = abs(((cQuantity * cRate) + (quantity * rate)) / nQuantity)
        nRateInfl = abs(((cQuantity * cRateInfl) + (quantity * rateInfl)) / nQuantity)
        nXRate = abs(((cQuantity * cXRate) + (quantity * xRate)) / nQuantity)
        nXRateInfl = abs(((cQuantity * cXRateInfl) + (quantity * xRateInfl)) / nQuantity)
    else:
        nRate = rate
        nRateInfl = rateInfl
        nXRate = xRate
        nXRateInfl = xRateInfl
    nBundle = iDate, fDate, nQuantity, nRate, nRateInfl, nXRate, nXRateInfl
    valueIntoDictionary(nBundle, holdings, account, ticker)

def valueIntoDictionary(val, dic, keyA, keyB):
    if keyA in dic.keys():
        dic[keyA][keyB] = val
    else:
        dic[keyA] = dict({keyB : val})

def getRate(dic, keyA, keyB):
    return getCurrent(dic, keyA, keyB)[5]

def getCurrent(dic, keyA, keyB):
    if keyA in dic.keys():
        if keyB in dic[keyA].keys():
            return dic[keyA][keyB]
    return ("", "", cD(0), cD(0), cD(0), cD(0), cD(0))

def loadAndProcessTransactions(xlsxFileName, cpis, databaseHost, databaseUser, databasePassword, database,
                               currentDate=dt.datetime.today(), dailySummary=False):
    mydb = sql.connect(
        host = databaseHost,
        user = databaseUser,
        password = databasePassword,
        database = database
    )
    transactionsFrame = loadTransactions(xlsxFileName)
    return processTransactions(transactionsFrame, dailySummary, cpis, currentDate, mydb.cursor())
