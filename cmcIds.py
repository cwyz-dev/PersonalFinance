from    coinmarketcapapi    import  CoinMarketCapAPI
import pandas as pd

coinMarketCapApiKey = ""
cmcIdCsvFile = "cmcIds.csv"

api = CoinMarketCapAPI(coinMarketCapApiKey)
idMap = api.cryptocurrency_map()
df = pd.DataFrame(idMap.data,
                  columns=["symbol", "name", "id", "slug", "is_active"])
df = df.sort_values(by=["symbol", "name"])
df.set_index("symbol", inplace=True)
df.to_csv(cmcIdCsvFile)
