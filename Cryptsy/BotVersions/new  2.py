import Cryptsy
import time
Exchange = Cryptsy.Cryptsy('no', 'no')
print(Exchange.getSingleMarketData(132))     

