#from    customNumber               import  customDecimal               as  cD
from decimal import Decimal as cD
from    customTiming                import  formatDateTime              as  fdt
from    customTiming                import  formatTimeDelta             as  ftd
from    transactionProcessing       import loadAndProcessTransactions   as  lapt
from    priceGathering              import  addPricesToFrame            as  aptf

import  datetime                                                        as  dt
import  os
import  pandas                                                          as  pd
import  xlsxwriter
import sys

defaultTransactionFile = "transactions.xlsx"
defaultOutputFile = "holdings.xlsx"
databaseHost = "localhost"
databaseUser = "root"
databasePassword = "MySQLRoot"
databaseName = "finances"

def writeTupleToXLSX(worksheet, row, index, data):
    for i in range(len(index)):
        worksheet.write(row, index[i], data[i])

def saveToXLSXFile(holdings, gains, outputFile, containsMarketData):
    if os.path.exists(outputFile):
        os.remove(outputFile)
    workbook = xlsxwriter.Workbook(outputFile)
    worksheet = workbook.add_worksheet()

    i = 0
    worksheetIndexes = (0,1,2,3,4,6,7,8,9,10)
    for account in sorted(holdings.keys()):
        for asset in sorted(holdings[account].keys()):
            pD = holdings[account][asset]
            marketData = ""
            if (containsMarketData):
                marketData = float(pD[7])
                a, b, c, d, e, f, g, _ = pD
            else:
                a, b, c, d, e, f, g = pD
            if c != "":
                c = float(c)
            else:
                c = float(0)
            if d != "":
                d = float(d)
            else:
                d = float(0)
            if e != "":
                e = float(e)
            else:
                e = float(0)
            if f != "":
                f = float(f)
            else:
                f = float(0)
            if g != "":
                g = float(g)
            else:
                g = float(0)
            data = (account, asset, a, b, c, d, e, g, g, marketData)
            writeTupleToXLSX(worksheet, i, worksheetIndexes, data)
            
            i += 1
    worksheet.write(i, 0, "TotalCapGains")
    worksheet.write(i, 4, gains["total"])
    worksheet.write(i+1, 0, "TaxableCapGains")
    worksheet.write(i+1, 4, gains["taxable"])
    workbook.close()

def main(transactionFile=defaultTransactionFile, outputFile=defaultOutputFile,
         precision=defaultPrecision, date=dt.datetime.today(), gatherPrice=True, verbose=True):
    cpiDict = dict({
        "2017": dict({
            "01": cD("129.5"), "02": cD("129.7"), "03": cD("129.9"), "04": cD("130.4"),
            "05": cD("130.5"), "06": cD("130.4"), "07": cD("130.4"), "08": cD("130.5"),
            "09": cD("130.8"), "10": cD("130.9"), "11": cD("131.3"), "12": cD("130.8")
	}),

	"2018": dict({
            "01": cD("131.7"), "02": cD("132.5"), "03": cD("132.9"), "04": cD("133.3"),
            "05": cD("133.4"), "06": cD("133.6"), "07": cD("134.3"), "08": cD("134.2"),
            "09": cD("133.7"), "10": cD("134.1"), "11": cD("133.5"), "12": cD("133.4")
	}),

	"2019": dict({
            "01": cD("133.6"), "02": cD("134.5"), "03": cD("135.4"), "04": cD("136.0"),
            "05": cD("136.6"), "06": cD("136.3"), "07": cD("137.0"), "08": cD("136.8"),
            "09": cD("136.2"), "10": cD("136.6"), "11": cD("136.4"), "12": cD("136.4")
	}),

	"2020": dict({
            "01": cD("136.8"), "02": cD("137.4"), "03": cD("136.6"), "04": cD("135.7"),
            "05": cD("136.1"), "06": cD("137.2"), "07": cD("137.2"), "08": cD("137.0"),
            "09": cD("136.9"), "10": cD("137.5"), "11": cD("137.7"), "12": cD("137.4")
	}),

	"2021": dict({
            "01": cD("138.2"), "02": cD("138.9"), "03": cD("139.6"), "04": cD("140.3"),
            "05": cD("141.0"), "06": cD("141.4"), "07": cD("142.3"), "08": cD("142.6"),
            "09": cD("142.9"), "10": cD("143.9"), "11": cD("144.2"), "12": cD("144")
	}),

	"2022": dict({
            "01": cD("145.3"), "02": cD("146.8"), "03": cD("148.9"), "04": cD("149.8"),
            "05": cD("151.9"), "06": cD("152.9"), "07": cD("153.1"), "08": cD("152.6"),
            "09": cD("152.7"), "10": cD("153.8"),
            "11": cD("153.8"), "12": cD("153.8")
	}),
    })    

    if (verbose):
        start = dt.datetime.now()
        print("Started at: " + fdt(start))
    currentHoldings, gains, dailyHoldings = lapt(transactionFile, cpiDict, databaseHost, databaseUser,
                                                 databasePassword, databaseName, date)
    if (gatherPrice):
        aptf(currentHoldings, date)
    saveToXLSXFile(currentHoldings, gains, outputFile, gatherPrice)
    if (verbose):
        end = dt.datetime.now()
        print("Ended at:" + fdt(end))
        print("Took: " + ftd(end - start))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(date=dt.datetime.strptime(f"{sys.argv[1]}-01-01 00:00:00.00000", "%Y-%m-%d %H:%M:%S.%f"))
    else:
        main(date=dt.datetime.today())
