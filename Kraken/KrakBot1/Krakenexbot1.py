import math
import time
import json
import krakenex
import argparse
#import pdb

#pdb.set_trace();

k = krakenex.api.API();
k.load_key('tradingbot1.key');

parser = argparse.ArgumentParser(description = 'a program that does something');
parser.add_argument("marketid", help = 'ID number of market you want to trade in', type=int,default=132);
parser.add_argument('amount', help = 'trade amount',type=int, default=500);
parser.add_argument('bias', help = 'trading profit bias',type=float, default=.5);
parser.add_argument('min_price_diff', help = 'how far from closed order to put new ones',type=float, default=1.0051);
args = parser.parse_args();

marketid = args.marketid
trade_amnt = float(args.amount)
delay = 15;
partial_threshold = float(.995);
count = 100;
errflag = 0;
print time.ctime();

bias = args.bias;
min_price_diff = args.min_price_diff;

#define my functions here:

class MyError(Exception):
	def __init__(self,value):
		self.value = value;
	def __str__(self):	
		return repr(self.value);
		


# this one takes the JSON return from the server, checks it for errors, and prints what they are into a file if they exist, also returns whether there was one or not.
#assumes only to be checking Kraken returns as of currently
def error_check( jsonreturn):
	flag = 0;
	if jsonreturn['error'] != []:
		#we have an error!
		f = open('Krakenexbot1_errors.txt','a');
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

#load last transaction timestamp
last_checked_timestamp = 0;
f = open('lastchecked.stamp','r');
last_checked_timestamp = float(f.readline());
f.close();

while count > 0:
	count = count - 1 ;
	servertime = k.query_public('Time');
	time.sleep(1);
	errflag = error_check(servertime);
	servertime = servertime['result']['unixtime'];
	time.sleep(.15);
	closeds = k.query_private('ClosedOrders',{'start':str(last_checked_timestamp-1),'trades':'true'})
	errflag = errflag or error_check(closeds);
	time.sleep(1);
	
	if errflag:
		#we have an error in closeds! will build this section out as i see what the errors are
		print str(closeds['error']);
		raise MyError('an error in closeds!');
	elif (int(closeds['result']['count']) <1):
		
		time.sleep(1.2);
		
		'''elif int(closeds['result']['count']) == 1: #this means one trade went through
	
		#get the price this one went through
		key = str(closeds['result']['closed'].keys()[0]);
		price = float(closeds['result']['closed'][key]['price']); 
		
		
		
		
		#put in new orders
		
		#update timestamp file
		a;
		elif int(closeds['result']['count']) == 2:
		
		#maybe use depth and start over?
		#or just check for last one? really, this is kinda bad. 
		#maybe just treat them like i used to for the Cryptsy bot one at a time?
		pass;'''
	else:
		
		
		#grab only the orders that count as proper closed orders, whatever proper means
		closedkeys = closeds['result']['closed'].keys();
		filledorderkeys={}; #these are the orders we're going to worry about, dict of (closetime: key)
		sortedfilleds = (); #sort filled orders by closed timestamp
		tradeids = [];
		tradeids_str = '';
		for key in closedkeys:
			
			#essentially a large switch case for all the different statuses
			#only those 'closed' and 'canceled' can be put in, and only some of 'canceled'
			if closeds['result']['closed'][key]['status'] == 'closed':
				filledorderkeys[ float(closeds['result']['closed'][key]['closetm']) ] = key;
				#add the key somewhere
				#add all trades associated to the trades list to ask the server about
				tradeids.extend(closeds['result']['closed'][key]['trades']);
			elif closeds['result']['closed'][key]['status'] == 'canceled':
				valids_set = {'Insignificant volume remaining'};
				invalids_set ={'User canceled', 'Cannot trade with self'};
				if closeds['result']['closed'][key]['reason'] in valids_set:
					filledorderkeys[ float(closeds['result']['closed'][key]['closetm']) ] = key;
					tradeids.extend(closeds['result']['closed'][key]['trades']);
				elif closeds['result']['closed'][key]['reason'] in invalids_set:
					if closeds['result']['closed'][key]['reason'] == 'Cannot trade with self':
						redo_order = k.query_private('AddOrder',{'pair':'XBTXDG','type':str(closeds['result']['closed'][key]['descr']['type']),'ordertype':'limit','price':str(closeds['result']['closed'][key]['descr']['price']),'volume':str(closeds['result']['closed'][key]['vol']),'oflags':'viqc'});
						time.sleep(1);
						errflag = errflag or error_check(redo_order);
						if errflag:
							raise MyError('new sell order fail');
						
						#also need to deal with market priced trades, currently tossing an error
					
					
					
					
					if closeds['result']['closed'][key]['reason'] == 'User canceled':
						#here we check to see whether we cancelled the order because it was basically filled but Kraken didn't do it for me
						executed = float(closeds['result']['closed'][key]['vol_exec']);
						total = float(closeds['result']['closed'][key]['vol']);
						if executed/total >= partial_threshold:
							filledorderkeys[ float(closeds['result']['closed'][key]['closetm']) ] = key;
							tradeids.extend(closeds['result']['closed'][key]['trades']);
				else:
					raise MyError('closed canceled order has unknown reason: '+str(closeds['result']['closed'][key]['reason']))
			elif closeds['result']['closed'][key]['status'] == 'expired':
				#it should be able to get here at a future date
				raise  MyError('closed order has expired status: '+str(key));
			elif closeds['result']['closed'][key]['status'] == 'open':
				#it should not get here normally
				raise  MyError('closed order has open status: '+str(key));
			elif closeds['result']['closed'][key]['status'] == 'pending':
				#it should not get here normally
				raise  MyError('closed order has pending status: '+str(key));
			else:
				#it should not get here at all
				raise  MyError('closed order has unaccounted for status'+str(key));
		
		#################################
		#now make a list of the sorted timestamps, as roundabout way of sorting the orders by time
		sortedfilleds = sorted(filledorderkeys);
		
		###########################
		#next grab the specifics of all the trades
		for item in tradeids:
			tradeids_str=tradeids_str+','+str(item);
		#remove leading comma cause idk how else to do this
		tradeids_str=tradeids_str[1:len(tradeids_str)];
		if len(tradeids)>0:
			trades = k.query_private('QueryTrades',{'txid':tradeids_str});
			time.sleep(1);

		#now if there are any orders left, we have to do stuff!
		while len(sortedfilleds)>0:
			print('entered valid closeds loop');
			print( sortedfilleds);
		
			#next we cancel all open orders and put in new ones
			
			#start with getting the open orders
			opens = k.query_private('OpenOrders');
			time.sleep(1);
			errflag = errflag or error_check(opens);
			openkeys = opens['result']['open'].keys();
			
			#in case theres an error, we want to quit this loop before we start fucking shit up
			if errflag:
				break;
			
			#grab the first proper closed order
			currenttime = sortedfilleds.pop(0);
			if math.ceil(currenttime) >= servertime:
				servertime = currenttime + 1;
			
			currentkey = filledorderkeys[currenttime];
			#thie line below cannot be trusted, the avg price they return is a lie
			#currentprice = float(closeds['result']['closed'][currentkey]['price']);
			#heres the easiest way i found to get the total price
			currentprice = 0;
			tradescopy = closeds['result']['closed'][currentkey]['trades'];
			currentvol = float(closeds['result']['closed'][currentkey]['vol_exec']);
			for tradeid in tradescopy:
				tradevol = float(trades['result'][tradeid]['cost']);
				tradeprice = float(trades['result'][tradeid]['price']);
				currentprice = currentprice+tradevol*(tradeprice/currentvol);
				
			print currentprice;
			
			#cancel the current orders
			while len(openkeys)>0:
				canceled = k.query_private('CancelOrder',{'txid': openkeys.pop()});
				time.sleep(7);
				errflag = errflag or error_check(canceled);
				
			#create a new buy and sell order
			buyprice = str(currentprice/min_price_diff);
			sellprice = str(currentprice*min_price_diff);
			sell_amount = str(trade_amnt+(trade_amnt*(min_price_diff-1.005)*bias));
			buy_amount = str(trade_amnt);

			new_buy = k.query_private('AddOrder',{'pair':'XBTXDG','type':'buy','ordertype':'limit','price':buyprice,'volume':buy_amount,'oflags':'viqc'});
			time.sleep(1);
			errflag = errflag or error_check(new_buy);
			if errflag:
				raise MyError('new buy order fail');
				
			new_sell = k.query_private('AddOrder',{'pair':'XBTXDG','type':'sell','ordertype':'limit','price':sellprice,'volume':sell_amount,'oflags':'viqc'});
			time.sleep(1);
			errflag = errflag or error_check(new_sell);
			if errflag:
				raise MyError('new sell order fail');
		
			time.sleep(3);
		
		
	time.sleep(2)
	#here we cancel any open orders that are mostly executed
	#start with getting the open orders
	opens = k.query_private('OpenOrders');
	time.sleep(1);
	errflag = errflag or error_check(opens);
	openkeys = opens['result']['open'].keys();
	
	for key in openkeys:
		total = float(opens['result']['open'][key]['vol']);
		executed = float(opens['result']['open'][key]['vol_exec']);
		if (executed/total >= partial_threshold):
			k.query_private('CancelOrder',{'txid':str(key)});
			time.sleep(2);
		
	
	
	#update last checked timestamp
	last_checked_timestamp = servertime;
	f = open('lastchecked.stamp','w');
	f.write(str(servertime));
	f.close();
	time.sleep(10);
				














