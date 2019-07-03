import math
import Cryptsy
import time
Exchange = Cryptsy.Cryptsy('Feel Free to', 'i closed the account');
doge_const = 132; #Dogecoin = 132
trade_amnt = 100; #how many doge per trade, 100 minimum)
last_processed_trade = Exchange.myTrades( doge_const, 1)['return'][0]; #returns most recent trade as of startup
unprocessed_trades = 0; #number of trades that have not yet been accounted for

 
while True:
	print "Unprocessed at top " +str(unprocessed_trades);
	my_recent_trades = Exchange.myTrades(doge_const, 100)['return']; # last 100 successful  transactions
	
	#now find out how many new trades happened since last check
	for index, returns in enumerate(my_recent_trades):
		if int(returns['timestamp']) == last_processed_trade['timestamp']:
			unprocessed_trades = index;
			print index;
			break;
			# if last processed is most recent transaction, index =0 and we dont need to do anything

	while unprocessed_trades > 0.01:
		new_type = 'blah';
		new_price = 0;
		unprocessed_trades = unprocessed_trades - 1;
		#grab the oldest unprocessed trade, call it current
		current_trade = my_recent_trades[unprocessed_trades];
		current_price = current_trade['tradeprice'];
		current_type = current_trade['tradetype'];
		if current_type == 'Buy':
			new_type = 'Sell';
			new_price = math.ceil[(100000000*float(current_price))*1.00501]/100000000;
			Exchange.createOrder(doge_const, new_type, trade_amnt , new_price);
		elif current_type == 'Sell':
			new_type = 'Buy';
			new_price = math.floor[(100000000*float(current_price))/1.00501]/100000000;
			Exchange.createOrder(doge_const, new_type, trade_amnt , new_price);
		print "Unprocessed Trades: " +str(unprocessed_trades);
		print "Current: " + str(current_type) + "at price "+str(current_price); 
		print "New    : " + str(new_type) + "at price "+str(new_price); 
	time.sleep(15);	
	print index;