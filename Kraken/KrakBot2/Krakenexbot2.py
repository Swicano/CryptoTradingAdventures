import math
import time
import json
import krakenex
##XXXimport argparse
#Lines preceded by '##XXX' were never used in this program but not removed in case i wanted to do something with them later
##XXXimport pdb

##XXXpdb.set_trace();

k = krakenex.api.API();
k.load_key('Krakenexbot2\profitbot2.key');

##XXXparser = argparse.ArgumentParser(description = 'a program that does something');
##XXXparser.add_argument("marketid", help = 'ID number of market you want to trade in', type=int,default=132);
##XXXparser.add_argument('amount', help = 'trade amount',type=int, default=500);
##XXXparser.add_argument('bias', help = 'trading profit bias',type=float, default=.5);
##XXXparser.add_argument('min_price_diff', help = 'how far from closed order to put new ones',type=float, default=1.0051);
##XXXargs = parser.parse_args();

##XXXmarketid = args.marketid
##XXXtrade_amnt = float(args.amount)
##XXXdelay = 15;
##xxxpartial_threshold = float(.995);
##xxxcount = 100;
errflag = 0;
errfile = 'Krakenexbot2\Krakenexbot2_errors.txt';

##xxxbias = args.bias;
##xxxmin_price_diff = args.min_price_diff;

#define my functions here:

class MyError(Exception):
	def __init__(self,value):
		self.value = value;
	def __str__(self):	
		return repr(self.value);
		


# this one takes the JSON return from the server, checks it for errors, and prints what they are into a file if they exist, also returns whether there was one or not.
#assumes only to be checking Kraken returns as of currently
def error_check( jsonreturn, error_file_path):
	flag = 0;
	if jsonreturn['error'] != []:
		#we have an error!
		f = open(error_file_path,'a');
		f.write(str(time.ctime())+"\n");
		f.write(str(jsonreturn['error'])+"\n");
		f.write(str(jsonreturn)+"\n"+"\n");
		f.close();
		flag = 1;
		raise MyError('error_checker '+str(jsonreturn['error']))
	return flag;


#float(k.query_public('Time')['result']['unixtime'])-time.time() is usually 4.7 - 5!
#k.query_public('Depth',{'pair':'XBTXDG','count':'2'})
#>>>k.query_private('AddOrder',{'pair':'XBTXDG','type':'sell','ordertype':'limit','price':'810000','volume':'100','oflags':'viqc','validate':'true'})
#{u'result': {u'descr': {u'order': u'sell 100.00000000 (XDG) XBTXDG @ limit 810000.0'}}, u'error': []}

#k.query_private('CancelOrder',{'txid':'properidnumber'})
#{u'result': {u'count': 1}, u'error': []}

#k.query_private('AddOrder',{'pair':'XBTXDG','type':'buy','ordertype':'limit','price':'710000','volume':'100','oflags':'viqc'})
#{u'result': {u'descr': {u'order': u'buy 100.00000000 (XDG) XBTXDG @ limit 710000.0'}, u'txid': [u'OS5WZK-DKDWZ-PHKZ2K']}, u'error': []}


#Grab current balances from kraken

balance = k.query_private('Balance');
time.sleep(1);
errflag = errflag or error_check(balance, errfile );
balance = balance['result']; #now balance is a dict of all the balances in string form though

#grab all deposits and make an equitable dict, deposits_dict

deposits = k.query_private('Ledgers',{'type':'deposit'});
time.sleep(1);
errflag = errflag or error_check(deposits,errfile);
deposits = deposits['result']['ledger'];
depositkeys = deposits.keys();
deposit_dict = {};
for key in depositkeys:
	if deposits[key]['asset'] in deposit_dict:
		deposit_dict[deposits[key]['asset']] = str(float(deposit_dict[deposits[key]['asset']]) +float(deposits[key]['amount']))
	else:
		deposit_dict[deposits[key]['asset']] = str(deposits[key]['amount']);
		
#create withdrawal dict in the same fashion as input

withdrawals = k.query_private('Ledgers',{'type':'withdrawal'});
time.sleep(1);
errflag = errflag or error_check(withdrawals,errfile);
withdrawals = withdrawals['result']['ledger'];
withdrawalkeys = withdrawals.keys();
withdrawal_dict = {};
for key in withdrawalkeys:
	if withdrawals[key]['asset'] in withdrawal_dict:
		withdrawal_dict[withdrawals[key]['asset']] = str(float(withdrawal_dict[withdrawals[key]['asset']]) +float(withdrawals[key]['amount']))
	else:
		withdrawal_dict[withdrawals[key]['asset']] = str(withdrawals[key]['amount']);
		
#now create trade_free_balance dict, which is deposits - withdrawals, or what the balance would be if i never made a single trade

trade_free_balances = {};
for key in withdrawal_dict.viewkeys()|deposit_dict.viewkeys():
	trade_free_balances[key] = float(deposit_dict.get(key,0))-float(withdrawal_dict.get(key,0));

#the differential is where i stand now relative to where i started, its the bits i need to 'undo' before calling something a 'profit'

differential = {};
for key in balance.viewkeys()|trade_free_balances.viewkeys():
	differential[key] = float( balance.get(key,0))-float(trade_free_balances.get(key,0));
	
#get prices! have form of dict of { assetpair : {'bid':bidprice , 'ask':askprice}}
#everything other than BTC will be converted to BTC and BTC will be converted into ZUSD

prices = {};
for key in differential:
	if key == 'XXBT':
		spread = k.query_public('Spread',{'pair':'XXBTZUSD'});
		time.sleep(1);
		errflag = errflag or error_check(spread,errfile);
		spread = spread['result']['XXBTZUSD'][len(spread['result']['XXBTZUSD'])-1];
		prices[key] ={'bid':spread[1],'ask':spread[2]};
	elif key == 'ZUSD':
		pass;
	else:
		assetpair = 'XXBT'+key;
		spread = k.query_public('Spread',{'pair':assetpair});
		time.sleep(1);
		errflag = errflag or error_check(spread,errfile);
		spread = spread['result'][assetpair][len(spread['result'][assetpair])-1];
		prices[key] ={'bid':spread[1],'ask':spread[2]};

# convert non BTC coins to BTC, then BTC to USD
btc_bal = 0;
for key in differential:
	if key == 'XXBT':
		btc_bal += differential[key];
	else:
		#check whether we need to 'buy' or 'sell' to zero out this currency
		if differential[key] >0: #differential being positive means i need to sell, so take highest bid
			converted_bal =float(differential[key])/float(prices[key]['bid']);
			btc_bal += converted_bal;
		else:
			converted_bal =float(differential[key])/float(prices[key]['ask']);
			btc_bal += converted_bal;

usd_bal=0;			
if btc_bal >0:
	usd_bal=btc_bal*float(prices['XXBT']['bid']);
else:
	usd_bal=btc_bal*float(prices['XXBT']['ask']);
		
print usd_bal;
f= open('krakenexbot2\profitskrak.csv','a');
f.write(time.ctime()+' , ');
f.write(str(usd_bal)+' , '+str(btc_bal)+' , ');
f.write(str(prices['XXBT']['bid'])+' , '+str(prices['XXBT']['ask'])+' , '+str(differential['XXBT'])+' , ');
f.write(str(prices['XLTC']['bid'])+' , '+str(prices['XLTC']['ask'])+' , '+str(differential['XLTC'])+' , ');
f.write(str(prices['XXDG']['bid'])+' , '+str(prices['XXDG']['ask'])+' , '+str(differential['XXDG'])+' \n');
f.close();



	
	
	
	
	
	
	
	
	
	
	
	









