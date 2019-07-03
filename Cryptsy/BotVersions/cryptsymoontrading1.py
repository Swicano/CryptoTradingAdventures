import math
import Cryptsy
import time
import json


Exchange = Cryptsy.Cryptsy('kjhgfds', 'ertyulihkgg');
doge_const = 145; #Dogecoin/btc = 132, tips/ltc = 147 , moon/ltc = 145
trade_amnt = 800; #how many doge per trade, 100 minimum)
bias = .5; #from 0-1, pick fraction of extra money that goes toward nonBTC/LTC currency (ie in doge/btc, bias =1 puts all profits into doge)

unprocessed_trades = 0; #number of trades that have not yet been accounted for
logs= open('MOONlog.txt' , 'a');
transacts = open('MOONtransactions.txt','a');
jasonread = open('MOONlasttrans.json','r+');
last_processed_trades = json.load(jasonread);
jasonread.close();

 
while True:
	print time.ctime();
	logs.write(str(time.ctime())+"\n");
	myTrades = {'success' : 0,'return':'qwerty'};
	while not int(myTrades['success']):
		try:
			myTrades = Exchange.myTrades(doge_const, 25); # last 100 successful  transactions
			print 'success at recent';
		except:
			print 'failed my_recent_trades';
			
	my_recent_trades = myTrades['return'];		
	
	
	#now find out how many new trades happened since last check
	for index, returns in enumerate(my_recent_trades):
		if returns['tradeid'] == last_processed_trades[0]['tradeid']:
			unprocessed_trades = index;
			print "Index of last trade = "+str(index);
			logs.write("Index of last trade = "+str(index)+"\n");
			break;
			# if last processed is most recent transaction, index =0 and we dont need to do anything during this while loop

	while unprocessed_trades > 0.01:
		new_type = 'blah';
		new_price = 0;
		partial_transact =0;
		#grab the oldest unprocessed trade, call it current
		current_trade = my_recent_trades[unprocessed_trades-1];
		json.dump(current_trade,transacts);
		transacts.write(',');
		current_price = current_trade['tradeprice'];
		current_type = current_trade['tradetype'];
		#check to see whether the current_trade is part of a split order that has already been processed (within the last 5 trades)
		for trade in last_processed_trades:
			if (trade['order_id'] == current_trade['order_id']):
				partial_transact = 1;
				break;		
		if partial_transact:
			print 'partial transaction';
			#do nothing this time around, since this order was already processed
		elif current_type == 'Buy':
			new_type = 'Sell';
			new_price = math.ceil((100000000*float(current_price))*1.00501)/100000000;
			bias_trade_amnt = trade_amnt;
		elif current_type == 'Sell':
			new_type = 'Buy';
			new_price = math.floor((100000000*float(current_price))/1.00501)/100000000;
			bias_trade_amnt =float(trade_amnt)+ float(trade_amnt)*((float(current_price)/float(new_price))-1.005)*bias;
		new_order = {'success':0,'moreinfo':'initialed new_order','orderid':123456789} ;
		while ((not int(new_order['success'])) and ( not partial_transact)):
			try:
				new_order = Exchange.createOrder(doge_const, new_type, bias_trade_amnt , new_price);
				print ' success at new order: ', new_order;
			except:
				print 'failed new order creation';
		if int(new_order['success']) or partial_transact:		
			unprocessed_trades = unprocessed_trades - 1;

			#update processed trades list
			last_processed_trades.pop();
			last_processed_trades.insert(0, current_trade);
		
			#write last_processed_trades to file
			jasonfile = open('MOONlasttrans.json','w');
			json.dump( last_processed_trades, jasonfile);
			jasonfile.close();
		
			#print logging stuff
			print "Unprocessed Trades: " +str(unprocessed_trades);
			logs.write("Unprocessed Trades: " +str(unprocessed_trades)+"\n");
			print "Current: " + str(current_type) + " at price "+str(current_price);
			logs.write("Current: " + str(current_type) +" "+current_trade['quantity']+ " at price "+str(current_price)+"\n");	
			print "New    : " + str(new_order['moreinfo']);
			logs.write("New    : " + str(new_order['moreinfo']));
	time.sleep(10);	
	print "Unprocessed at end "+str(unprocessed_trades);
logs.close();
transacts.close();
jasonfile.close();