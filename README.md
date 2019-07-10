# Crypto Trading

This collection of scripts served 2 purposes, to learn about programmatic interaction with websites (API stuff) as well as to try out the simplest possible trading algorithm: buy low, sell high, if a profit exists, make the trade. a more thorough mathematical exploration of the pros and cons will come later, once I figure out how to write math in markdown. 

Cryptsy and Kraken are two different trading platforms, but the base algorithm is essentially the same, the significant difference is the API interaction code, as well as minor improvements. Kraken is more up to date

The code ran for several months on each platform, performing over 5000 automated trades on the Kraken platform, which resulted in quadrupling my Dogecoin holdings, though both proved ultimately unsustainable due to large scale price changes. The algorithm does not respond well to large scale price changes and is designed to work on a stable, but noisy exchange price, extracting profit in exchange for liquidity.
