#from	customDecimalProcessing import 	customDecimalProcessor 	as cdp
#from    customNumber            import  customDecimal           as  cD
from decimal import Decimal as cD
from kuCoinParser import getTimeStamp, getCryptoValue, customSleep

from    coinmarketcapapi        import  CoinMarketCapAPI
from    time            	import  sleep
from    easy_exchange_rates     import  API                     as exchangeAPI

import  datetime                                                as  dt
import  pandas                                                  as  pd
import  pandas_datareader                                       as  pd_dr

baseForeignCurrencies = dict({
    "EUR": 0,
    "USD": 0
})

baseCryptos = dict({
    "1INCH": [8104, 0], "ALGO": [4030, 0], "AMP": [6945, 0], "ANKR": [3783, 0], "AUCTION": [8602, 0],
    "AVA": [2776, 0], "AVAX": [5805, 0], "AXS": [6783, 0], "BAL": [5728, 0], "BETH": [8353, 0],
    "BNB": [1839, 0], "BOND": [7440, 0], "BTC": [1, 0], "BUSD": [4687, 0], "CAKE": [7186, 0],
    "CELO": [5567, 0], "CHZ": [4066, 0], "CITY": [10049, 0], "CKB": [4948, 0], "CLV": [8384, 0],
    "COMP": [5692, 0], "CTSI": [5444, 0], "DAI": [4943, 0], "DAR": [11374, 0], "DOT": [6636, 0],
    "DXCT": [11211, 0], "ETH": [1027, 0], "FET": [3773, 0], "FORTH": [9421, 0], "GRT": [6719, 0],
    "KLAY": [4256, 0], "LRC": [1934, 0], "MATIC": [3890, 0], "MBOX": [9175, 0], "NEXO": [2694, 0],
    "NU": [4761, 0], "RAMP": [7463, 0], "RLY": [8075, 0], "SAND": [6210, 0], "SKL": [5691, 0],
    "SMON": [11523, 0], "SUSHI": [6758, 0], "USDT": [825, 0], "XLM": [512, 0], "XMS": [10030, 0],
    "XTZ": [2011, 0], "YOOSHI": [9892, 0], "QI": [9288, 0], "DOGE": [74, 0], "LTC": [2, 0],
    "SHIB": [5994, 0], "YFI": [5864, 0], "AAVE": [7278, 0], "ADA": [2010, 0], "ATOM": [3794, 0],
    "BAT": [1697, 0], "BCH": [1831, 0], "CRV": [6538, 0], "FIL": [2280, 0], "FTM": [3513, 0],
    "KNC": [9444, 0], "LINK": [1975, 0], "MANA": [1966, 0], "MKR": [1518, 0], "REN": [2539, 0],
    "SNX": [2586, 0], "SOL": [5426, 0], "UMA": [5617, 0], "UNI": [7083, 0], "ZRX": [1896, 0],
    "SANTOS": [15248, 0], "IOTX": [2777, 0], "MC": [13523, 0], "QNT": [3155, 0], "HIGH": [11232, 0],
    "NEAR": [6535, 0], "RUN": [15754, 0], "FLOW": [4558, 0], "ANC": [8857, 0], "JASMY": [8425, 0],
    "ENJ": [2130, 0], "CTX": [10368, 0], "RNDR": [5690, 0], "LUNA": [20314, 0], "GALA": [7080, 0],
    "MBS": [13011, 0], "ACA": [6756, 0], "GMX": [11857, 0], "USDC": [3408, 0], "MV": [17704, 0],
    "UST": [7129, 0], "APE": [18876, 0], "DYDX": [11156, 0], "GAL": [11877, 0], "MINA": [8646, 0],
    "LUNC": [4172, 0], "ERN": [8615, 0], "BNT": [1727, 0], "CHR": [3978, 0], "STORJ": [1772, 0],
    "WAMPL": [17610, 0], "SG": [6245, 0], "METIS": [9640, 0], "LEVER": [20873, 0], "BAND": [4679, 0],
    "COTI": [3992, 0], "PAXG": [4705, 0], "ALEPH": [5821, 0], "HOPR": [6520, 0], "EOS": [1765, 0],
    "HBAR": [4642, 0], "XCN": [18679, ""], "ETHW": [21296, 0], "00": [22142, ""], "HFT": [22461, 0],
    "RAY": [8526, 0], "SHPING": [3422, ""]
})

baseLiquidityPools = dict({
    "AVA/BTC":      (cD(1.079)      / cD(0.00545114)),
    "DXCT/BUSD":    (cD(7.69)       / cD(9.53048213405373)),    # Not active any more
    "ETH/BETH":     (cD(11.2881)    / cD(0.00476293)),
    "RAMP/BUSD":    (cD(14.0879)    / cD(30.50660723)),         # Not active any more
    "RAY/USDT":     (cD(7.1109)     / cD(7.68886956)),          # Not active any more
    "SAND/BNB":     (cD(0.6943)     / cD(0.02708974)),
    "SMON/BUSD":    (cD(25.34)      / cD(4.10082273415546)),    # Not active any more
    "XMS/BNB":      (cD(0.47)       / cD(0.201640853)),         # Not active any more
    "YOOSHI/BNB":   (cD(99.71)      / cD(0.0907341199674133)),  # Not active any more
    "BUSD/BNB":     (cD(35.56)       / cD(0.770287308397592952))
})

baseStocks = dict({
    "TSE:SVI": 0, "NASDAQ:AAPL": 0, "NASDAQ:AMZN": 0, "NASDAQ:COIN": 0, "NASDAQ:META": 0,
    "NASDAQ:GOOGL": 0, "NASDAQ:INTC": 0, "NASDAQ:MSFT": 0, "NASDAQ:NFLX": "", "NASDAQ:NVDA": 0,
    "NASDAQ:QCOM": 0, "NASDAQ:TSLA": 0, "NYSE:ORCL": 0, "TSE:BIP.UN": 0, "TSE:BNS": 0,
    "TSE:CRT.UN": 0, "TSE:GRT.UN": 0, "TSE:RNW": 0, "TSE:VCN": 0, "TSE:ZLB": 0, "TSE:ZSP": 0,
    "TSE:VIU": 0, "CVE:BTCW": 0, "TSE:ZRE": 0, "TSE:ZLI": 0, "TSE:T": 0, "TSE:SU": 0, "NYSE:BA": 0,
    "TSE:CWB": 0, "TSE:MR.UN": 0, "TSE:FCR.UN": 0
})

stringDateTimeFormat = "%Y-%m-%d %H:%M:%S"
stringDateFormat = "%Y-%m-%d"
coinMarketCapApiKey = ""
canadianDollar = "CAD"
unitedStatesDollar = "USD"

def getForeignCurrencyValues(assets, foreignCurrencies, date=dt.datetime.today()):
    forexApi = exchangeAPI()
    for ticker in foreignCurrencies.keys():
        if (ticker in assets):
            foreignCurrencies[ticker] = getForexCurrencyRate(forexApi, ticker, date)

def getForexCurrencyRate(forexApi, currency, date):
    try:
        dateString = date.strftime(stringDateFormat)
        result = forexApi.get_exchange_rates(base_currency=currency, start_date=dateString,
                                             end_date=dateString, targets=[canadianDollar])
        #return cdp(str(result[dateString][canadianDollar]))
        return cD(str(result[dateString][canadianDollar]))
    except:
        return getForexCurrencyRate(forexApi, currency, date - dt.timedelta(days=1))

def getCryptoValueDate(cmcApi, ticker, cmcId, date, cycles=0):
    val = 0
    try:
        if date < dt.datetime.combine(dt.date.today(), dt.datetime.min.time()):
            return getCryptoValue(ticker, date.timestamp())
        else:
            return (cmcApi.tools_priceconversion(amount=1, id=cmcId, convert=canadianDollar).data)['quote'][canadianDollar]['price']
    except:
        if cycles < 100:
            customSleep(0.1, 0.1)
            return getCryptoValueDate(cmcApi, ticker, cmcId, date - dt.timedelta(days=1), cycles + 1)
        else:
            return 0
    

def getCryptoValues(assets, cryptos, date=dt.datetime.today()):
    cmcApi = CoinMarketCapAPI(coinMarketCapApiKey)
    for ticker in cryptos.keys():
        if ticker in assets:
            customSleep(2,2)
            cryptos[ticker][1] = cD(str(getCryptoValueDate(cmcApi, ticker, cryptos[ticker][0], date)))

def getLiquidityPoolValues(assets, liquidityPools, foreignCurrencies):
    for ticker in liquidityPools:
        if (ticker in assets):
            liquidityPools[ticker] = cD(liquidityPools[ticker]) * foreignCurrencies[unitedStatesDollar]
        
def getStockValues(assets, stocks, foreignCurrencies, datetime):
    for ticker in stocks.keys():
        if (ticker in assets):
            value = getYahooStockPrice(tickerToYahooTicker(ticker), datetime)
            if (isAssetUSStock(ticker)):
                value *= foreignCurrencies[unitedStatesDollar]
            stocks[ticker] = value

def tickerToYahooTicker(ticker):
    output = ""
    if (ticker[:3] == "TSE"):
        output = ticker[4:].replace(".", "-") + ".TO"
    elif (ticker[:3] == "CVE"):
        output = ticker[4:].replace(".", "-") + ".V"
    elif (ticker[:6] == "NASDAQ"):
        output = ticker[7:].replace(".", "-")
    elif (ticker[:4] == "NYSE"):
        output = ticker[5:].replace(".", "-")

    return output

def getYahooStockPrice(yahooTicker, datetime):
    try:
        readData = pd_dr.data.DataReader(yahooTicker, 'yahoo', datetime.strftime(stringDateFormat),
                                         datetime.strftime(stringDateFormat))
        return cD(str(readData["Close"][0].item()))
    except BaseException as err:
        return getYahooStockPrice(yahooTicker, datetime - dt.timedelta(days=1))

def gatherPriceData(assets, foreignCurrencies, cryptos, liquidityPools, stocks, datetime):
    getForeignCurrencyValues(assets, foreignCurrencies, datetime)
    getCryptoValues(assets, cryptos, datetime)
    getLiquidityPoolValues(assets, liquidityPools, foreignCurrencies)
    getStockValues(assets, stocks, foreignCurrencies, datetime)

def isAssetUSStock(ticker):
    if (ticker[:6] == "NASDAQ" or ticker[:4] == "NYSE"):
        return True
    return False

def isAssetUSStockOrLiquidityPool(asset, liquidityPools):
    if (isAssetUSStock(asset)):
        return True
    elif (asset in liquidityPools):
        return True
    return False

def addAssetToDict(assetDict, asset, liquidityPools):
    if (not(asset in assetDict)):
        if (asset != unitedStatesDollar):
            if (isAssetUSStockOrLiquidityPool(asset, liquidityPools)):
                addAssetToDict(assetDict, unitedStatesDollar, liquidityPools)
        assetDict[asset] = ""

def getAllAssets(holdings, liquidityPools):
    allAssets = dict()
    for account in holdings:
        for asset in holdings[account]:
            #if (not(cdp(holdings[account][asset][2], op="isZero"))):
            if holdings[account][asset][2] != 0:
                addAssetToDict(allAssets, asset, liquidityPools)
    return allAssets

def appendPricesToFrame(holdings, foreignCurrencies, cryptos, liquidityPools, stocks):
    for account in holdings:
        for asset in holdings[account]:
            val = ""
            if (asset in foreignCurrencies):
                val = foreignCurrencies[asset]
            elif (asset in cryptos):
                 val = cryptos[asset][1]
            elif (asset in liquidityPools):
                val = liquidityPools[asset]
            elif (asset in stocks):
                val = stocks[asset]
            else:
                val = holdings[account][asset][4]
            holdings[account][asset] += (val, )

def addPricesToFrame(holdings, datetime, foreignCurrencies=baseForeignCurrencies,
                         cryptos=baseCryptos, liquidityPools=baseLiquidityPools, stocks=baseStocks):
    allAssets = getAllAssets(holdings, liquidityPools)
    gatherPriceData(allAssets, foreignCurrencies, cryptos, liquidityPools, stocks, datetime)
    appendPricesToFrame(holdings, foreignCurrencies, cryptos, liquidityPools, stocks)

if __name__ == "__main__":
    #holdings = dict({"X": dict({"TSE:RNW": ("","",15,cdp("1"),cdp("1")),
    #                            #"BTC": ("", "", 1, cdp("50000"),cdp("55000")),
    #                            #"A/B": ("","",0.2, cdp("1"),cdp("16.8")),
    #                            "EUR": ("","",500,cdp("2"),cdp("2.1"))})})
    #addPricesToFrame(holdings, dt.datetime.today())
    #print(holdings)
    x = 1
