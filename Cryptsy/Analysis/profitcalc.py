import math
import Cryptsy
import time
import json
import os.path
import urllib2


Exchange = Cryptsy.Cryptsy('gggggggggggggggg', 'ggggggggggggggggggggggg');


#________________________________________________Grab all extternal transactions to account
mytransacts = {'success' : 0,'return':'qwerty'};
while not int(mytransacts['success']):
	try:
		mytransacts = Exchange.myTransactions(); # last external transactions
	except Exception as inst:
		print 'failed my_recent_transacts: ', type(inst);
		#logs.write(time.ctime()+': Recent trade failed: '+str(type(inst))+str(inst)+'\n');
	else:
		print 'success at recent trades';
my_recent_transacts = mytransacts['return'];
deposits={};
for item in my_recent_transacts:
	if item['type']=='Withdrawal':
		item['amount'] = str(-1*float(item['amount']));
	if item['currency'] in deposits:
		deposits[item['currency']]= float(deposits[item['currency']])+float(item['amount']);
	else:
		deposits[item['currency']]=item['amount'];
'''
		
LTCdeposits = .09359852;
TIPSdeposits = 700000+70152;
dogedeposits = 4000+2000+2000+1000+400+6000+3000+1500+3303;
BTCdeposits = .00194149+.024+.02+.03;
moondeposits = 0;
deposits = {'LTC':LTCdeposits,'TIPS':TIPSdeposits,'DOGE':dogedeposits,'BTC':BTCdeposits,'MOON':moondeposits};
'''
#_________________________________________________grab all the current balances from Cryptsy
mybalances = {'success' : 0,'return':'qwerty'};
while not int(mybalances['success']):
	try:
		mybalances = Exchange.getInfo(); # last 25 successful  transactions
	except Exception as inst:
		print 'failed my_recent_trades: ', type(inst);
		#logs.write(time.ctime()+': Recent trade failed: '+str(type(inst))+str(inst)+'\n');
	else:
		print 'success at recent trades';
		
my_recent_balances = mybalances['return'];

#__________________________________________________Add up the held and available balances
#__________________________________________________ assumption that i have something held in all currencies!!!
#__________________________________________________find differential right now since less loops

held = my_recent_balances['balances_hold'];
available = my_recent_balances['balances_available'];
total_balances = {};
differential = {'LTC':0,'TIPS':0,'MOON':0}; #	total balance - deposits
for item in held:
	total_balances[item]= float(held[item])+float(available[item]);
	if item in deposits:
		differential[item] = float(total_balances[item]) - float(deposits[item]);
	else:
		differential[item] = float(total_balances[item])
		
#____________________________________________________Get Prices

prices = {};
for item in differential:
	if os.path.isfile(str(item)+'lasttrans.json'):
		lasttransname = str(item)+'lasttrans.json';
		jasonread = open(lasttransname,'r+');
		last_processed_trades = json.load(jasonread);
		jasonread.close();
		prices[item] = float(last_processed_trades[0]['tradeprice']);
	elif item == 'BTC':
		req = urllib2.Request('http://api.bitcoincharts.com/v1/weighted_prices.json');
		response = urllib2.urlopen(req);
		page = response.read();
		the_page = json.loads(page);
		prices[item] = float(the_page['USD']['7d']);
	elif item == 'LTC':
		depth = {'success' : 0,'return':'qwerty'};
		while not int(depth['success']):
			try:
				depth = Exchange.depth(3); # last external transactions
			except Exception as inst:
				print 'failed ltc depth: ', type(inst);
			else:
				print 'success at recent trades';
		prices[item] = float(depth['return']['sell'][0][0]);
	elif item == 'QRK':
		depth = {'success' : 0,'return':'qwerty'};
		while not int(depth['success']):
			try:
				depth = Exchange.depth(71); # last external transactions
			except Exception as inst:
				print 'failed ltc depth: ', type(inst);
			else:
				print 'success at recent trades';
		prices[item] = float(depth['return']['sell'][0][0]);
	else:
		prices[item] = float(raw_input('Enter current '+str(item)+' rate: '));

value_once = {} # differential*price
for item in differential:
	value_once[item] = differential[item]*prices[item];

differential_two ={};
differential_two['LTC'] = differential['LTC']+value_once['TIPS']+value_once['MOON'];
differential_two['BTC'] = differential['BTC']+value_once['DOGE'];

differential_three = {};
differential_three['BTC'] = differential_two['BTC']+differential_two['LTC']*prices['LTC']

profit = differential_three['BTC']*prices['BTC'];

print profit;

f= open('profits.csv','a');
f.write(time.ctime()+' , ');
f.write(str(profit)+' , '+str(differential_three['BTC'])+' , ');
f.write(str(prices['BTC'])+' , '+str(differential['BTC'])+' , ');
f.write(str(prices['LTC'])+' , '+str(differential['LTC'])+' , ');
f.write(str(prices['DOGE'])+' , '+str(differential['DOGE'])+' , ');
f.write(str(prices['TIPS'])+' , '+str(differential['TIPS'])+' , ');
f.write(str(prices['MOON'])+' , '+str(differential['MOON'])+' \n');
f.close();


	

#time.sleep(15);