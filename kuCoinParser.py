#from	customDecimalProcessing     import  customDecimalProcessor  as cdp
#from    customNumber                import  customDecimal       as cD
from decimal import Decimal as cD
from    customTiming                import  formatDateTime      as fdt
from    customTiming                import  formatTimeDelta     as ftd

from    kucoin.client               import  Margin
from    kucoin.client               import  User
from    time                        import  sleep

import  datetime                                                as  dt
import  json
import  math
import  os
import  pandas                                                  as  pd
import  random
import  requests
import  sys
import  urllib
import  xlsxwriter


precision = 8
today = dt.datetime.now()
minDate = dt.datetime(2022, 1, 1)
errorLimit = 10

# TODO: Break this out, it is super helpful
def customSleep(midWait, variance, minWait=0, minTimeForGroup=0, group=[]):
    if len(group) == 0:
        group = [0]
    groupTime = 0
    zeroes = 0
    for call in group:
        groupTime += call
        if (call == 0):
            zeroes += 1
    minTimeForGroup = minTimeForGroup * ((len(group)-zeroes) / len(group))
    minWait = max(midWait, (minTimeForGroup - groupTime))
    time = max(minWait, abs(random.gauss(minWait, variance)))
    sleep(time)
    return time

# TODO: Break this out, it is super helpful
def roundToHour(dTime):
    if dTime.minute >= 30:
        dTime = dTime + dt.timedelta(hours=1)
    dTime = dTime.replace(minute=0,second=0)
    return dTime.timestamp()

# TODO: Break this out, it is super helpful
def roundToDay(dTime):
    if dTime.hour > 12:
        dTime = dTime + dt.timedelta(days=1)
    dTime = dTime.replace(hour=0,minute=0,second=0)
    return dTime.timestamp()

# TODO: Break this out, it is super helpful
def getTimeStamp(timestamp):
    dTime = timestamp.to_pydatetime()
    if ((today - dTime).days > 30):
        return roundToDay(dTime)
    else:
        return roundToHour(dTime)

def getCryptoValue(ticker, timestamp):
    apiKey = ""
    query = str("https://min-api.cryptocompare.com/data/v2/histohour?fsym=" + ticker + "&tsym=CAD&limit=1&toTs=" +
                str(timestamp) + "&api_key" + apiKey)
    response = requests.get(query)
    return cD(response.json()["Data"]["Data"][0]["close"])

def getCryptoTimesDict(frames):
    cryptos = dict({})
    for i in range(len(frames)):
        for index, item in frames[i].iterrows():
            token = item["token"]
            time = getTimeStamp(item["date"])
            if (not(token in cryptos.keys())):
                cryptos[token] = dict({time: getCryptoValue(token, time)})
                customSleep(2,2)
            elif (not(time in cryptos[token].keys())):
                cryptos[token][time] = getCryptoValue(token, time)
                customSleep(2,2)
    return cryptos

def writeToXLSX(loans, repayments):
    start = dt.datetime.now()
    print("Starting value collection at " + fdt(start))
    
    values = getCryptoTimesDict([loans, repayments])

    end = dt.datetime.now()
    print("Finished value collection, took " + ftd(end - start) + ", gathered  " + str(len(values)) +
          " cryptos, and ended at " + fdt(end))
    
    start = dt.datetime.now()
    print("Starting writing to XLSX at " + fdt(start))
    if os.path.exists("kCTransactions.xlsx"):
        os.remove("kCTransactions.xlsx")
    workbook = xlsxwriter.Workbook("kCTransactions.xlsx")
    worksheet = workbook.add_worksheet()

    i = 0
    for index, transaction in loans.iterrows():
        rate = values[transaction["token"]][getTimeStamp(transaction["date"])]
        worksheet.write(i,0,transaction["date"])
        worksheet.write(i,1,"KuCoin - Main")
        worksheet.write(i,2,transaction["token"])
        worksheet.write(i,3,transaction["quantity"])
        worksheet.write(i,4,rate)
        worksheet.write(i,6,transaction["date"])
        worksheet.write(i,7,"KuCoin - Lending (Debt)")
        worksheet.write(i,8,transaction["token"])
        worksheet.write(i,9,transaction["quantity"])
        worksheet.write(i,10,rate)
        worksheet.write(i,13,"Transfer")
        worksheet.write(i,14,"Lending "+transaction["token"]+" @ "+str(transaction["rate"])+
                        " % interest for "+str(transaction["term"])+" days")
        i += 1

    for index, transaction in repayments.iterrows():
        rate = float(values[transaction["token"]][getTimeStamp(transaction["date"])])

        if transaction["principal"] != 0:
            worksheet.write(i,0,transaction["date"])
            worksheet.write(i,1,"KuCoin - Lending (Debt)")
            worksheet.write(i,2,transaction["token"])
            worksheet.write(i,3,float(transaction["principal"]))
            worksheet.write(i,4,rate)
            worksheet.write(i,6,transaction["date"])
            worksheet.write(i,7,"KuCoin - Main")
            worksheet.write(i,8,transaction["token"])
            worksheet.write(i,9,float(transaction["principal"]))
            worksheet.write(i,10,rate)
            worksheet.write(i,13,"Transfer")
            worksheet.write(i,14,"Early loan repayment")
            i += 1

        if transaction["interest"] != 0:
            worksheet.write(i,6,transaction["date"])
            worksheet.write(i,7,"KuCoin - Main")
            worksheet.write(i,8,transaction["token"])
            worksheet.write(i,9,float(transaction["interest"]))
            worksheet.write(i,10,rate)
            worksheet.write(i,13,"Payment")
            worksheet.write(i,14,"Interest on loan")
            i += 1

    workbook.close()
    
    end = dt.datetime.now()
    print("Finished writing to XLSX, took " + ftd(end - start) + ", wrote  " + str(i) + " lines, and ended at "
          + fdt(end))

# TODO: Break this out, it is super helpful
def roundTimestampToSeconds(time):
    dTime = dt.datetime.fromtimestamp(time/1000)
    if dTime.microsecond >= 500000:
        dTime = dTime + dt.timedelta(seconds=1)
    return dTime.replace(microsecond=0)

# TODO: Break this out, it is super helpful
def formatDates(df, dateCol):
    df[dateCol] = df[dateCol].apply(lambda x: roundTimestampToSeconds(x))
    return df

def getRecursiveUnsettledLoans(client, sleeptime=2, iterations=[], currentPage=1, pageSize=50, errorCount=0):
    if (errorCount == errorLimit):
        return pd.DataFrame({"": []})
    slept = customSleep(sleeptime, sleeptime/2, sleeptime/6, sleeptime*len(iterations), iterations)
    try:
        rawUnsettled = client.get_active_list(currentPage=currentPage, pageSize=pageSize)
    except:
        customSleep(20, 10)
        return getRecursiveUnsettledLoans(client, sleeptime + 0.5, iterations, currentPage, pageSize,
                                          errorCount + 1)
    unsettled = pd.DataFrame(columns=["tradeId", "currency", "size", "accrusedInterest", "repaid", "dailyIntRate",
                                      "term", "maturityTime"])
    if len(rawUnsettled["items"]) > 0:
        unsettled = unsettled.append(formatDates(pd.json_normalize(rawUnsettled["items"]), "maturityTime"))
        totalPage = rawUnsettled["totalPage"]
        if (totalPage != currentPage):
            iterations.append(slept)
            unsettled = unsettled.append(getRecursiveUnsettledLoans(client, sleeptime, iterations, currentPage + 1,
                                                                    pageSize))
    return unsettled

def getUnsettledLoans(client):
    unsettled = getRecursiveUnsettledLoans(client)
    unsettled = unsettled.sort_values(by=["maturityTime", "size", "currency"])
    unsettled.reset_index(drop=True, inplace=True)
    unsettled["size"] = unsettled["repaid"].apply(lambda x: cD(x))
    unsettled["repaid"] = unsettled["repaid"].apply(lambda x: cD(x))
    return unsettled

def getRecursiveSettledLoans(client, sleeptime=2, iterations=[], currentPage=1, pageSize=50, errorCount=0):
    if (errorCount == errorLimit):
        return pd.DataFrame({"": []})
    slept = customSleep(sleeptime, sleeptime/2, sleeptime/6, sleeptime*len(iterations), iterations)
    try:
        rawSettled = client.get_settled_order(currentPage=currentPage, pageSize=pageSize)
    except:
        customSleep(20, 10)
        return getRecursiveSettledLoans(client, sleeptime + 0.5, iterations, currentPage, pageSize, errorCount + 1)
    settled = pd.DataFrame(columns=["tradeId", "currency", "size", "interest", "repaid", "dailyIntRate", "term",
                                    "settledAt", "note"])
    settled = settled.append(formatDates(pd.json_normalize(rawSettled["items"]), "settledAt"))
    totalPage = rawSettled["totalPage"]
    if (totalPage != currentPage):
        iterations.append(slept)
        settled = settled.append(getRecursiveSettledLoans(client, sleeptime, iterations, currentPage + 1, pageSize))
    return settled

def getSettledLoans(client):
    settled = getRecursiveSettledLoans(client)
    settled = settled.sort_values(by=["settledAt", "size", "currency"])
    settled.reset_index(drop=True, inplace=True)
    settled["size"] = settled["size"].apply(lambda x: cD(x))
    settled["repaid"] = settled["repaid"].apply(lambda x: cD(x))
    settled["dailyIntRate"] = settled["dailyIntRate"].apply(lambda x: cD(x) * 100)
    return settled

def getRecursiveLedgers(datetime, client, sleeptime=2, iterations=[], currentPage=1, pageSize=100, errorCount=0):
    transactions = pd.DataFrame(columns=["id", "currency", "amount", "fee", "balance", "accountType",
                                         "bizType", "direction", "createdAt", "context"])
    if (datetime < minDate or errorCount == errorLimit):
        return transactions
    slept = customSleep(sleeptime*2.5, sleeptime/2, sleeptime/3, sleeptime*len(iterations), iterations)
    try:
        rawTransactions = client.get_account_ledger(endAt=int(datetime.timestamp()*1000), currentPage=currentPage,
                                                    pageSize=pageSize)
        iterations.append(slept)
        totalPage = rawTransactions["totalPage"]
        if (totalPage == 0):
            transactions = transactions.append(getRecursiveLedgers(datetime - dt.timedelta(days=1), client,
                                                                   sleeptime, iterations, currentPage, pageSize))
        else:
            transactions = transactions.append(formatDates(pd.json_normalize(rawTransactions["items"]),
                                                           "createdAt"),
                                               ignore_index=True)
            if (currentPage != totalPage):
                transactions = transactions.append(getRecursiveLedgers(datetime, client, sleeptime, iterations,
                                                                       currentPage + 1, pageSize))            
            if (currentPage == 1):
                transactions = transactions.append(getRecursiveLedgers(datetime - dt.timedelta(days=1), client,
                                                                       sleeptime, iterations, currentPage,
                                                                       pageSize))
        return transactions
    except:
        customSleep(20.001, 1, 15)
        return transactions.append(getRecursiveLedgers(datetime, client, sleeptime + 0.5, iterations, currentPage,
                                                       pageSize, errorCount + 1))

def getLedgers(client):
    transactions = getRecursiveLedgers(today, client)
    transactions = transactions[transactions["bizType"].str.contains("Loan")]
    transactions = transactions.sort_values(by=["createdAt", "amount", "currency"])
    transactions.reset_index(drop=True, inplace=True)
    transactions["amount"] = transactions["amount"].apply(lambda x: cD(x))
    return transactions

def recursiveSingleCheck(target, index, row):
    if row["amount"] == target:
        return [index]
    return []

# TODO: Find improved algorithms, Naive recursive solution currently
def recursiveFind(target, transactions, maxDepth):
    # If there's no items, return
    if (transactions.shape[0] == 0):
        return []
    # If there's only one item, check it and return
    elif (transactions.shape[0] == 1):
        for i, t in transactions.iterrows():
            return recursiveSingleCheck(target, i, t)
    
    transactions = transactions.sort_values(by=["createdAt", "amount"])
    if (transactions.shape[0] > maxDepth):
        skip = True
        
        # Check the top and bottom transactions up to depth 1 or 2
        if (maxDepth < 3):
            inUses = recursiveFind(target, transactions.head(maxDepth), maxDepth)
            if (len(inUses) > 0):
                return inUses
            inUses = recursiveFind(target, transactions.tail(maxDepth), maxDepth)
            if (len(inUses) > 0):
                return inUses
        # Check the top and bottom transactions up to 1/3 of the maxDepth each
        elif (maxDepth > 2):
            newDepth = math.floor(maxDepth / 3)
            inUses = recursiveFind(target, transactions.head(newDepth), newDepth)
            if (len(inUses) > 0):
                return inUses
            inUses = recursiveFind(target, transactions.tail(newDepth), newDepth)
            if (len(inUses) > 0):
                return inUses

        # Odds that we do a full check
        if (maxDepth > 0):
            if (random.randrange(1, math.ceil((maxDepth+1)/2)+1, 1) == 1):
               skip = False
            #skip = False
        if (skip):
            return []
    
    for i, t in transactions.iterrows():
        try:
            return [recursiveSingleCheck(target, i, t)[0]]
        except:
            if t["amount"] < target:
                newTarget = target - t["amount"]
                if newTarget != 0:
                    temp = transactions[(transactions["createdAt"] >= t["createdAt"]) & (transactions["id"] != t["id"])]
                    temp = temp.sort_values(by=["createdAt", "amount"])
                    temp = temp[temp["amount"].apply(lambda x: x <= newTarget)]
                    inUses = recursiveFind(newTarget, temp, maxDepth - 1)
                    if (len(inUses) > 0):
                        inUses.append(i)
                        return inUses
    return []

def main(depth):
    apiKey = ""
    apiSecret = ""
    apiPassPhrase = ""
    
    start = dt.datetime.now()
    print("Starting data gathering at " + fdt(start))

    marginClient = Margin(apiKey, secret=apiSecret, passphrase=apiPassPhrase, is_sandbox=False,
                          url='https://api.kucoin.com')
    unsettled = getUnsettledLoans(marginClient)
    customSleep(20, 0.01, 12)
    settled = getSettledLoans(marginClient)

    customSleep(20, 0.01, 12)
    transactions = getLedgers(User(apiKey, secret=apiSecret, passphrase=apiPassPhrase, is_sandbox=False))
    outTransactions = transactions[transactions["direction"] == "out"].copy()
    inTransactions = transactions[transactions["direction"] == "in"].copy()
    loans = pd.DataFrame(columns=["date", "token", "quantity", "rate", "term"])
    repays = pd.DataFrame(columns=["date", "token", "principal", "interest"])

    previousSize = outTransactions.shape[0]
    modified = False
    prevModified = False
    totalLoans = outTransactions.shape[0]

    end = dt.datetime.now()
    print("Finished data gathering, took " + ftd(end - start) + ", gathered  " + str(totalLoans) + ", and ended at "
          + fdt(end))
    print("Starting evaluations...")
    print("-----")
    passCount = 1
    activeDepth = 0
    while (True):
        start = dt.datetime.now()
        print("Starting pass " + str(passCount) + ", with " + str(outTransactions.shape[0]) + " loans remaining, at " +
              fdt(start))
        modified = False
        
        # Loop through transactions for settled loans
        if (settled.shape[0] > 0 and outTransactions.shape[0] > 0):
            if (settled.shape[0] == 1 and outTransactions.shape[0] == 1):
                for si, st in settled.iterrows():
                    for oi, ot in outTransactions.iterrows():
                        for ii, it in inTransactions.iterrows():
                            proportion = i["amount"] / st["repaid"]
                            principal = proportion * ot["amount"]
                            interest = i["amount"] - principal
                            repays = repays.append({"date": it["createdAt"], "token": it["currency"],
                                                    "principal": principal, "interest": interest}, ignore_index=True)
                        loans = loans.append({"date": ot["createdAt"], "token": ot["currency"], "quantity": ot["amount"],
                                              "rate": st["dailyIntRate"], "term": st["term"]}, ignore_index=True)
                modified = True
            else:
                usedOuts = []
                for index, transaction in outTransactions.iterrows():
                    usedSettle = []
                    checkSettles = settled[(settled["currency"] == transaction["currency"]) &
                                       (settled["settledAt"] > transaction["createdAt"])]
                    checkSettles = checkSettles[checkSettles["size"].apply(lambda x: x == transaction["amount"])]
                    completed = False
                    for jndex, settle in checkSettles.iterrows():
                        if (transaction["currency"] == settle["currency"] and transaction["amount"] == settle["size"]):
                            atEnd = inTransactions[(inTransactions["currency"] == transaction["currency"]) &
                                               (inTransactions["createdAt"] == settle["settledAt"])]
                            atEnd = atEnd.sort_values(by=["amount"])
                            atEnd = atEnd[atEnd["amount"].apply(lambda x: x <= settle["repaid"], "<=")]
                            for kndex, end in atEnd.iterrows():
                                if end["amount"] == settle["repaid"]:
                                    completed = True
                                    for lndex, i in inTransactions.iterrows():
                                        if (i["id"] == end["id"]):
                                            inTransactions.drop(index=lndex, inplace=True)
                                            break
                                    repays = repays.append({"date": end["createdAt"], "token": end["currency"],
                                                            "principal": transaction["amount"],
                                                            "interest": end["amount"] - transaction["amount"]},
                                                           ignore_index=True)
                                    break

                            if (not(completed) and activeDepth > 0):
                                for kndex, end in atEnd.iterrows():
                                    if end["amount"] < settle["repaid"]:
                                        target = settle["repaid"] - end["amount"]
                                        temp = inTransactions[(inTransactions["currency"] == transaction["currency"]) &
                                                              (inTransactions["createdAt"] > transaction["createdAt"]) &
                                                              (inTransactions["createdAt"] < end["createdAt"])]
                                        temp = temp.sort_values(by=["createdAt", "amount"])
                                        temp = temp[temp["amount"].apply(lambda x: x <= target)]
                                        usedIns = recursiveFind(target, temp, activeDepth)
                                        if (len(usedIns) > 0):
                                            completed = True
                                            usedIns.append(kndex)
                                            for lndex, i in inTransactions.iterrows():
                                                if (lndex in usedIns):
                                                    proportion = i["amount"] / settle["repaid"]
                                                    principal = proportion * transaction["amount"]
                                                    interest = i["amount"] - principal
                                                    repays = repays.append({"date": i["createdAt"],
                                                                            "token": i["currency"],
                                                                            "principal": principal,
                                                                            "interest": interest}, ignore_index=True)
                                            for used in usedIns:
                                                inTransactions.drop(index=used, inplace=True)
                                            break
                        if (completed):
                            usedOuts.insert(0, index)
                            usedSettle.insert(0, jndex)
                            loans = loans.append({"date": transaction["createdAt"], "token": transaction["currency"],
                                                  "quantity": transaction["amount"], "rate": settle["dailyIntRate"],
                                                  "term": settle["term"]}, ignore_index=True)
                            break
                    for used in usedSettle:
                        settled.drop(index=used, inplace=True)
                for used in usedOuts:
                    outTransactions.drop(index=used, inplace=True)
                    modified = True

        # Loop through for unsettled
        if (unsettled.shape[0] > 0 and outTransactions.shape[0] > 0):
            if (unsettled.shape[0] == 1 and outTransactions.shape[0] == 1):
                for ui, ut in unsettled.iterrows():
                    for oi, ot in outTransactions.iterrows():
                        for ii, it in inTransactions.iterrows():
                            proportion = it["amount"] / ut["repaid"]
                            principal = proportion * ot["amount"]
                            interest = it["amount"] - principal
                            repays = repays.append({"date": it["createdAt"], "token": it["currency"],
                                                    "principal": principal, "interest": interest}, ignore_index=True)
                            
                        loans = loans.append({"date": ot["createdAt"], "token": ot["currency"], "quantity": ot["amount"],
                                              "rate": st["dailyIntRate"], "term": st["term"]}, ignore_index=True)
                modified = True
            else:
                usedOuts = []
                for index, transaction in outTransactions.iterrows():
                    usedUnsettle = []
                    checkUnsettles = unsettled[(unsettled["currency"] == transaction["currency"]) &
                                               (unsettled["maturityTime"] > transaction["createdAt"])]
                    checkUnsettles = checkUnsettles[checkUnsettles["size"].apply(lambda x: x <= transaction["amount"])]
                    completed = False
                    for jndex, unsettle in checkUnsettles.iterrows():
                        if (transaction["currency"] == unsettle["currency"] and transaction["amount"] == unsettle["size"]):
                            if unsettle["repaid"] == 0:
                                completed = True
                            else:
                                available = inTransactions[inTransactions["currency"] == transaction["currency"]]
                                available = available[available["amount"].apply(lambda x: x <= unsettle["repaid"])]
                                usedIns = recursiveFind(unsettle["repaid"], available, activeDepth)
                                if (len(usedIns) > 0):
                                    completed = True
                                    usedIns.append(kndex)
                                    for lndex, i in inTransactions.iterrows():
                                        if (lndex in usedIns):
                                            principal = (i["amount"] / settle["repaid"]) * transaction["amount"]
                                            interest = i["amount"] - principal
                                            repays = repays.append({"date": i["createdAt"], "token": i["currency"],
                                                                    "principal": principal, "interest": interest},
                                                                   ignore_index=True)
                                        for used in usedIns:
                                            inTransactions.drop(index=used, inplace=True)
                        if (completed):
                            usedOuts.insert(0, index)
                            usedUnsettle.insert(0, jndex)
                            loans = loans.append({"date": transaction["createdAt"], "token": transaction["currency"],
                                                  "quantity": transaction["amount"], "rate": settle["dailyIntRate"],
                                                  "term": settle["term"]}, ignore_index=True)
                            break
                    for used in usedUnsettle:
                        unsettled.drop(index=used, inplace=True)
                for used in usedOuts:
                    outTransactions.drop(index=used, inplace=True)
                    modified = True

        end = dt.datetime.now()
        print("Pass " + str(passCount) + ", with depth " + str(activeDepth) + ", took " + ftd(end - start) +
              ", processed " + str(previousSize - outTransactions.shape[0]) + " transactions, and ended at " + fdt(end))

        # Check if we need to go again, if remaining transaction count is unchanged
        if ((not(modified) and not(prevModified) and activeDepth > (depth / 2)) or
            activeDepth >= depth or
            outTransactions.shape[0] == 0):
            break
        else:
            prevModified = modified
            previousRun = previousSize
            finalSize = outTransactions.shape[0]
            passCount = passCount + 1
            if (depth > activeDepth or depth == 0):
                val = 1
                if (not(modified) or (finalSize / previousSize) >= 0.95):
                    val = 2
                activeDepth = activeDepth + val
            previousSize = finalSize
    try:
        print("-----")
        print("Evaluations completed...")
        remainingLoans = outTransactions.shape[0]
        print("Unrectified loans: " + str(remainingLoans) + ", equal to " + str((remainingLoans/totalLoans)*100) +
              " % remaining")
        remainingReturns = inTransactions.shape[0]
        print("Remaining returns: " + str(remainingReturns))
        start = dt.datetime.now()
        print("Starting final parsing at " + fdt(start))

        # Forcing the remaining, but without splitting gains
        for oi, ot in outTransactions.iterrows():
            loans = loans.append({"date": ot["createdAt"], "token": ot["currency"], "quantity": ot["amount"], "rate": "", "term": ""},
                                 ignore_index=True)
        for ii, it in inTransactions.iterrows():
            repays = repays.append({"date": it["createdAt"], "token": it["currency"], "principal": it["amount"], "interest": cD(0)},
                                   ignore_index=True)
        end = dt.datetime.now()
        print("Finished final parsing, took " + ftd(end - start) + ", parsed  " + str(remainingLoans) + " loans and " +
              str(remainingReturns) + " returns, and ended at " + fdt(end))
    except:
        pass
    writeToXLSX(loans, repays)

if __name__ == "__main__":
    start = dt.datetime.now()
    depth = 1
    if (len(sys.argv) > 1):
        depth = int(sys.argv[1])
    print("Started at " + fdt(start) + " with max depth of " + str(depth))
    main(depth)
    end = dt.datetime.now()
    print("Ended at " + fdt(end) + " and took " + ftd(end - start))
