import json
import list_bsc
from web3 import Web3
import urllib
from nested_lookup import nested_lookup
import requests
#for binance smart chain network
bsc = "https://bsc-dataseed.binance.org/"
url_eth = "https://api.bscscan.com/api"
web3 = Web3(Web3.HTTPProvider(bsc))


#from https://github.com/paowongsakorn/get_price_on_dex_BSC_Web3.py
def findPrice (factory, pair):

    #this is where my fn will be different and take in addresses
	AMM = list_bsc.module['AMM'][factory]['Factory']
	x = pair.split('/')
	Tokens1 = list_bsc.module['Tokens'][x[0]]
	Tokens2 = list_bsc.module['Tokens'][x[1]]


	web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
	Tokens1 = web3.to_checksum_address(Tokens1)
	Tokens2 = web3.to_checksum_address(Tokens2)
	Factory_Address = web3.to_checksum_address(AMM)


	#ABI Contract factory
	with open('src/factory.json', 'r') as abi_definition:
	    abi = json.load(abi_definition)


	#ABI Contract Pancake Pair
	with open('src/pair.json', 'r') as abi_definition:
	    parsed_pair = json.load(abi_definition)


	#####################################################################
	#####################################################################


	contract = web3.eth.contract(address=Factory_Address, abi=abi)
	pair_address = contract.functions.getPair(Tokens1,Tokens2).call()
	pair1 = web3.eth.contract(abi=parsed_pair, address=pair_address)


	reserves = pair1.functions.getReserves().call()
	reserve0 = reserves[0]
	reserve1  = reserves[1]


	print(f'The current {pair} price on {factory} is : ${reserve1/reserve0}')
	return (reserve0/reserve1)
	
	
#based on https://github.com/paowongsakorn/get_price_on_dex_BSC_Web3.py
#This fn takes a token address as a string an returns the value of the given 
#	token in dollar coins.
def getPrice (passed_token):
    factory="Twindex"
    #factory="Pancake"
    AMM = list_bsc.module['AMM'][factory]['Factory']
    Tokens1 = str(passed_token)
    #This is Binance dollar coin address
    Tokens2 = '0xe9e7cea3dedca5984780bafc599bd69add087d56'
    web3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
    Tokens1 = web3.to_checksum_address(Tokens1)
    Tokens2 = web3.to_checksum_address(Tokens2)
    Factory_Address = web3.to_checksum_address(AMM)
	#ABI Contract factory
    with open('src/factory.json', 'r') as abi_definition:
        abi = json.load(abi_definition)
	#ABI Contract Pancake Pair
    with open('src/pair.json', 'r') as abi_definition:
            parsed_pair = json.load(abi_definition)
    contract = web3.eth.contract(address=Factory_Address, abi=abi)
    pair_address = contract.functions.getPair(Tokens1,Tokens2).call()
    pair1 = web3.eth.contract(abi=parsed_pair, address=pair_address)
    reserves = pair1.functions.getReserves().call()
    reserve0 = reserves[0]
    reserve1  = reserves[1]
    #print(f'The current {pair} price on {factory} is : ${reserve1/reserve0}')
    #print("get price complete")
    return (reserve0/reserve1)



#This function takes a hexidecimal walletAddress and token address
#	as a string and returns the quantity of the given token in 
#	the passed wallet address.
#	Bug: If more than 5 requests are made in a second bscscan will
#		reject the request. 'request failed!' is printed to the
#		console of the server.
def getBalance(walletAddress, TokenAddress):
    #walletAddress = 0x531FEbfeb9a61D948c384ACFBe6dCc51057AEa7e
    #TokenAddress = 0x2170Ed0880ac9A755fd29B2688956BD959F933F8
    contract_address = web3.to_checksum_address(TokenAddress)
    API_ENDPOINT = url_eth+"?module=contract&action=getabi&address="+str(contract_address)
    r = requests.get(url = API_ENDPOINT)
    response = r.json()
    try:
       abi=json.loads(response["result"])
    except:
       print("request failed!")
       print(bscResponse)
    contract = web3.eth.contract(address=contract_address, abi=abi)
    totalSupply = contract.functions.totalSupply().call()
#    print(totalSupply)
#    print(contract.functions.name().call())
#    print(contract.functions.symbol().call())
    address = web3.to_checksum_address(walletAddress)
    balance=contract.functions.balanceOf(address).call()
#    print(web3.from_wei(balance, "ether"))
    return balance

#This function takes a hexidecimal walletAddress as a string
#	and returns a dictionary strings of all the tokens adresses
#	for all the tokens that have ever been in the given wallet.
#	Bug: If more than 5 requests are made in a second bscscan will
#		reject the request. 'request failed!' is printed to the
#		console of the server.
def getAllCurrency(walletAddress):
    #this wallet has alot of money in it. It may be used to test 
    #	the fn.
    #walletAddress = "0x531FEbfeb9a61D948c384ACFBe6dCc51057AEa7e"
    j_result = dict()
    processed_result = dict()
    #remove page=1 in production enviroment, this is to limit data
    #	to prevent free bscscan account request overload during 
    #	development.
    bscscanAPI = "https://api.bscscan.com/api?module=account&action=tokentx&page=1&offset=5&startblock=0&endblock=999999999&sort=asc&address="
    callBscScan = str(bscscanAPI + walletAddress)
    bscResponse = requests.get(callBscScan)
    try:
       j_result = bscResponse.json()
    except:
       print("request failed!")
       print(bscResponse)
    processed_result = (nested_lookup('contractAddress', j_result))
    #print(processed_result)
    #remove duplicates from processed result
    res = dict()
    #if processed_result.items():
    #   for key, val in processed_result.items():
    #      if val not in res.values():
    #         result[key] = value
    #   return res
    return processed_result

#This function takes a hexidecimal walletAddress as a string
#	and returns a dollar total of all the tokens in the given wallet.
#	Bug: If more than 5 requests are made in a second bscscan will
#		reject the request. 'request failed!' is printed to the
#		console of the server.
def calculateWalletValue(walletAddress):
	#for testing purposes only
    #walletAddress = "0x531FEbfeb9a61D948c384ACFBe6dCc51057AEa7e"
    tokens = dict()
    tokens = getAllCurrency(str(walletAddress))
    dollarTotal = float(0.0)
    for key in tokens:
        tokenBalance = float(0.0)
        tokenBalance = float(getBalance(str(walletAddress), key))
        if tokenBalance > 0:
            dollars = float(getPrice(key))
            dollarTotal += (tokenBalance * dollars)
    return dollarTotal
