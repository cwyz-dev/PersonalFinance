# Finance App
Created by: Christopher Wood

## Usage
This is a series of python scripts, meant to take in a log of transactions and output a "current state" after processing all transactions.
The code is run by executing the `main.py` python file. A year can be passed as an additional argument to only process transactions that occured before January 1 of that year (xxxx-01-01)

## Assumptions
The format of the transaction log is the following:
Sort Date |  | Asset Out Date | Asset Out Account | Asset Out Name | Asset Out Amount | Asset Out Rate (CAD) | | Asset In Date | Asset In Account | Asset In Name | Asset In Amount | Asset In Rate (CAD) | | Fee Amount | Transaction Type | Notes

Several API keys/secrets/passwords are needed to unlock the full functionality of the program. They are listed below
- KuCoin (used in kuCoinParser.py)
- min-api.cryptocompare.com (used in kuCoinParser.py)
- CoinMarketCap (used in priceGathering.py)

The system will expect a file named `transactions.xlsx` to exist in the folder.

The lists of potentially searched foreign currencies, cryptocurrencies, and stocks must be filled out in the `priceGathering.py` file.
Cryptocurrencies in `priceGathering.py` must have their CoinMarketCap unique ID included in the list for the cryptocurrency.
The list of liquidity pools and their value (in USD) must be filled out in `priceGathering.py`

## TODO List
- [x] Basic setup
- [] Database integration
- [] Pull unique/usefull functions into helper files
- [] Put customNumber into it's own repository
- [] Generalize code to improve use coverage
- [] Config files