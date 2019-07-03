import argparse
import math
import Cryptsy
import time
import json
import ast
#import pdb

#pdb.set_trace();


Exchange = Cryptsy.Cryptsy('ddddddddddddd', 'ddddddddddddddddddd');
markets={132:'DOGE',145:'MOON',147:'TIPS'};
originators = {0:'web',1:'this program, ', 2: 'this program, '};


parser = argparse.ArgumentParser(description = 'a program that does something');
parser.add_argument("marketid", help = 'ID number of market you want to trade in', type=int,default=132);
parser.add_argument('amount', help = 'trade amount',type=int, default=500);
parser.add_argument('bias', help = 'trading bias',type=float, default=.5);
args = parser.parse_args();

marketid = args.marketid
trade_amnt = args.amount
delay = 15;
partial_threshold = float(trade_amnt*.0005);
count = 1000;


bias = args.bias; #from 0-1, pick fraction of extra money that goes toward nonBTC/LTC currency (ie in doge/btc, bias =1 puts all profits into doge)
unprocessed_trades = 0; #number of trades that have not yet been accounted for in this program


#_______________________________________________________Opens the logging file to write to
logname = markets[marketid]+'log.txt';
logs= open(logname , 'a', 1);

#_______________________________________________________Opens the list of all transactions in this market to read it all in from, then later append to it
transactsname = markets[marketid]+'transactions.txt';
transacts = open(transactsname,'r');
alltransacts = transacts.read();
alltransacts = alltransacts[0:len(alltransacts)-1];
alltransacts = ast.literal_eval(alltransacts);
transacts.close();
transacts = open(transactsname,'a');

#_______________________________________________________Opens the recent transactoins list, 
#_______________________________________________________ short since opened and written often
lasttransname = markets[marketid]+'lasttrans.json';
jasonread = open(lasttransname,'r+');
last_processed_trades = json.load(jasonread);
jasonread.close();

#_______________________________________________________Opens the open orders file for this market
#_______________________________________________________ dict of {orderid : {order details}}
openname = markets[marketid]+'openorders.txt';
orders = open(openname,'r+');
local_open_orders = eval(orders.read());
orders.close();
ordercheckdelay = 2; # flag to not check open orders with Cryptsy ever iteration to save time
# since the open orders from cryptsy need to be made into a proper dict

 
while count > 0:
	count = count - 1 ;
	print time.ctime();

	
	#__________________________________________________Get most recent open orders from Cryptsy, if no checkdelay
	#__________________________________________________ currently erases local_open_orders and rewrites it
	#__________________________________________________ not sure if thats how i want to keep it, hence strange coding
	web_open_orders = []; #need this declared here so i can check against it later
	if ordercheckdelay == 0:
#		local_open_orders = {}; #this bit worries me
		logs.flush();
		logs.write(str(time.ctime())+"\n");
		myorders = {'success' : 0,'return':'qwerty'};
		while not int(myorders['success']):
			try:
				myorders = Exchange.myOrders(marketid); # all open orders in market
			except Exception as inst:
				print 'failed retrieve open orders: '+str(type(inst));
				logs.write(time.ctime()+': open orders failed: '+str(type(inst))+str(inst)+'\n');
			else:
				print 'success at open orders';
		web_open_orders = myorders['return'];
		for weborder in web_open_orders:
			if int(weborder['orderid']) in local_open_orders:
				pass; #heres where i would change things. if i was gonna
			else :
				local_open_orders[int(weborder['orderid'])] = weborder;
				local_open_orders[int(weborder['orderid'])]['originator'] = 0;
		if len(web_open_orders) < len(local_open_orders):
			#logs.write('extra open orders in local: '+str(len(local_open_orders)-len(web_open_orders))+'\n');
			#check to see if any local opens are also in closed transactions list, alltransacts
			duplicates = [];
			for order in local_open_orders:
				# but dont bother checking ones that are in web_open_locals since we know those should be there
				if order not in web_open_orders:
					if any(d.get('order_id', None) == str(order) for d in alltransacts):
						# this indicates an order is in local_open and the closed transaction file so it is a duplicate
						duplicates.append(order);
			# remove all duplicates from local_opens
			while len(duplicates)>0:
				local_open_orders.pop(duplicates.pop());
		if len(web_open_orders) < len(local_open_orders):
			print 'extra opens in local after checking for dupes: '+str(len(local_open_orders)-len(web_open_orders));
					
			
			
		ordercheckdelay = delay;
	ordercheckdelay = ordercheckdelay - 1;
	
	#___________________________________________________Gets newest list of finished trades from Cryptsy
	myTrades = {'success' : 0,'return':'qwerty'};
	while not int(myTrades['success']):
		try:
			myTrades = Exchange.myTrades(marketid, 100); # last 25 successful  transactions
		except Exception as inst:
			print 'failed my_recent_trades: ', type(inst);
			logs.write(time.ctime()+': Recent trade failed: '+str(type(inst))+str(inst)+'\n');
		else:
			print 'success at recent trades';
	my_recent_trades = myTrades['return'];		
	
	
	#___________________________________________________now find out how many new trades happened since last check
	for index, returns in enumerate(my_recent_trades):
		if returns['tradeid'] == last_processed_trades[0]['tradeid']:
			unprocessed_trades = index;
			print "Index of last trade = "+str(index);
			#logs.write("Index of last trade = "+str(index)+"\n");
			break;
			# if last processed is most recent transaction, index =0 and we dont need to do anything during this while loop
			
			
	#___________________________________________________THE FUCK LOOP
	while unprocessed_trades > 0.01:
		#_______________________________________________initialize some sweet sweet variables
		new_type = 'blah';
		new_price = 0;
		#partial_transact =0; #might be outdates soon.
		
		
		#_______________________________________________Grab the oldest unprocessed trade, call it current
		#_______________________________________________ current as in the one we're focusing on, clearly it's behind, add it to the total transaction list
		current_trade = my_recent_trades[unprocessed_trades-1];
		json.dump(current_trade,transacts);
		transacts.write(',');
		
		#_______________________________________________Check if it is not partial transaction
		current_orderid = int(current_trade['order_id']);
		if current_orderid in local_open_orders:
			local_open_orders[current_orderid]['quantity'] = float(local_open_orders[current_orderid]['quantity'])-float(current_trade['quantity']);
			if float(local_open_orders[current_orderid]['quantity']) < partial_threshold: 
			
				'''
				#_______________________________________ It's not a partial! but somehow broken...
				
				#_______________________________________Now we start forming the new order
				current_type = current_trade['tradetype'];
				current_price = float(local_open_orders[current_orderid]['price'])
				if current_type == 'Buy':
					new_type = 'Sell';
					new_price = math.ceil((100000000*float(current_price))*1.00501)/100000000;
					bias_trade_amnt = trade_amnt;
				elif current_type == 'Sell':
					new_type = 'Buy';
					new_price = math.floor((100000000*float(current_price))/1.00501)/100000000;
					bias_trade_amnt =float(trade_amnt)+ float(trade_amnt)*((float(current_price)/float(new_price))-1.005)*bias;
					
				#_______________________________________Try to get Crypsty to accept the order
				new_order = {'success':0,'moreinfo':'initialed new_order','orderid':123456789} ;
				while (not int(new_order['success'])) :
					try:
						new_order = Exchange.createOrder(marketid, new_type, bias_trade_amnt , new_price);
					except Exception as inst:
						print 'failed new order creation'+str(type(inst));
						logs.write(time.ctime()+': New Order Creation failed: '+str(type(inst))+str(inst)+'\n');
					else:
						if int(new_order['success']):
							print 'From current order: '+str(current_type)+' of '+str(local_open_orders[current_orderid]['orig_quantity'])+' at '+str(current_price)+' id: '+str(current_orderid);
							logs.write('From current order: '+str(current_type)+' of '+str(current_trade['quantity'])+' at '+str(current_price)+' id: '+str(current_orderid)+' and leaving '+str(local_open_orders[current_orderid]['quantity'])+' remaining \n');
							print ' success at new order: '+str(new_order['moreinfo']);
							logs.write('success at new order: '+str(new_order['moreinfo'])+'\n');
						else:
							print 'No error, but still not success! '+str(new_order);
							logs.write(time.ctime()+' No error, but still not success! '+str(new_order)+'\n');
						
				
				
				
				
				#_______________________________________Update open orders list
				length = len(local_open_orders);
				local_open_orders[int(new_order['orderid'])] = {'orderid':str(new_order['orderid']),'created': time.ctime(),'ordertype':new_type,'price':str(new_price),'total':str(new_price*bias_trade_amnt),'orig_quantity':str(bias_trade_amnt), 'quantity':str(bias_trade_amnt),'originator':1};
				pops = local_open_orders.pop(current_orderid, 1 );
				print 'popped: '+str(pops);
				if length != len(local_open_orders):
					logs.write( 'Length of local_open_orders increased by '+str(len(local_open_orders)-length));
				if current_orderid in local_open_orders:
					logs.write('current trade failed to pop, '+ str(current_trade));
				if int(new_order['orderid']) not in local_open_orders:
					logs.write('new order not added to list'+str(new_order));
				orders = open(openname,'w');
				orders.write(str(local_open_orders));
				orders.close();
				'''
					
			else:
				pass;
			
			
			#_______________________________________update processed trades list
			last_processed_trades.pop();
			last_processed_trades.insert(0, current_trade);
			#_______________________________________write last_processed_trades to file
			jasonfile = open(lasttransname,'w');
			json.dump( last_processed_trades, jasonfile);
			jasonfile.close();
					
		else:	#if it gets here something has gone terribly wrong. no wait, im a retard. thats totally normal on new open order starts
			logs.write('Current trade not in current open orders at: '+str(time.ctime())+'\n\n');
			print 'current not in opens';
			logs.write(str(current_trade)+'\n');
			if ordercheckdelay < (delay-1):
				ordercheckdelay = 0;
				unprocessed_trades =1;
			else:
				pass;
				#local_open_orders[int(current_trade['order_id'])] = {'orderid':str(current_trade['order_id']),'created': time.ctime(),'ordertype':current_trade['tradetype'],'price':current_trade['tradeprice'],'total':str(0),'orig_quantity':current_trade['quantity'], 'quantity':current_trade['quantity']};
		
			
		
		
		unprocessed_trades= unprocessed_trades-1;
		#print logging stuff
		print "Unprocessed Trades: " +str(unprocessed_trades);
#		logs.write("Unprocessed Trades: " +str(unprocessed_trades)+"\n");
#		print "Current: " + str(current_type) + " at price "+str(current_price);
#		logs.write("Current: " + str(current_type) +" "+current_trade['quantity']+ " at price "+str(current_price)+"\n");	
#		print "New    : " + str(new_order['moreinfo']);
#		logs.write("New    : " + str(new_order['moreinfo']));
	# the thought here is that if we check a new web opens, and nothing has changed, we can just dump all the opens we have saved locally and trust the web opens to be complete?
	if ordercheckdelay == delay - 1:
		myorders = {'success' : 0,'return':'qwerty'};
		while not int(myorders['success']):
			try:
				myorders = Exchange.myOrders(marketid); # all open orders in market
			except Exception as inst:
				print 'failed retrieve open orders: '+str(type(inst));
				logs.write(time.ctime()+': open orders failed: '+str(type(inst))+str(inst)+'\n');
			else:
				print 'success at open orders';
		web_open_orders2 = myorders['return'];
		if web_open_orders == web_open_orders2 and len(web_open_orders2) < len(local_open_orders):		
			duplicates = [];
			for order in local_open_orders:
				if order not in web_open_orders:
					duplicates.append(order);
			# remove all duplicates from local_opens
			print ' erasing '+str(len(duplicates))+' local opens not in web opens';
			while len(duplicates)>0:
				local_open_orders.pop(duplicates.pop());
	time.sleep(10);	
	print "Unprocessed at end "+str(unprocessed_trades);
	
orders = open(openname,'w');
orders.write(str(local_open_orders));
orders.close();
logs.close();
transacts.close();
#jasonfile.close();