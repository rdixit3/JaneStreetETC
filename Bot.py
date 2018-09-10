#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json
import time

#Configuration
team_name="OHCAMEL"
test_mode =False
test_exchange_index=0
prod_exchange_hostname="production"
port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

#Networking
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())

def bond(exchange):
    data = read_from_exchange(exchange)

    print(data)
    
    if data['type'] == 'book' and data['symbol'] == 'BOND':
        bids = data['buy']
        for price, size in bids:
            # if price > 1000:
            write_to_exchange(exchange, {"type": "add", "order_id": int(time.time()) , "symbol": "BOND", "dir": "SELL", "price": 1001, "size": 100})
        asks = data['sell']

        for price, size in asks:
            # if price < 1000:
            write_to_exchange(exchange, {"type": "add", "order_id": int(time.time()) , "symbol": "BOND", "dir": "BUY", "price": 999, "size": 100})

def get_price(bid, ask):
    bid_price_list = []
    ask_price_list = []

    for i in bid:
        bid_price_list.append(i[0])

    for i in ask:
        ask_price_list.append(i[0])
    
    highest_bid = max(bid_price_list)
    bid_avg = sum(bid_price_list)/len(bid_price_list)
    lowest_ask = min(ask_price_list)
    ask_avg = sum(ask_price_list)/len(ask_price_list)
    return [highest_bid, lowest_ask, bid_avg, ask_avg]

def pennying(exchange, stock):
    data = read_from_exchange(exchange)

    print(data)
    
    if data['type'] == 'book' and data['symbol'] == stock:
        bids = data['buy']
        asks = data['sell']

        [buy_at, sell_at, bid_avg, ask_avg] = get_price(bids, asks)
        
        if buy_at < (buy_at+sell_at)/2:
            write_to_exchange(exchange, {"type": "add", "order_id": int(time.time()) , "symbol": stock, "dir": "BUY", "price": buy_at+1, "size": 10})


        if sell_at > (buy_at+sell_at)/2:
            write_to_exchange(exchange, {"type": "add", "order_id": int(time.time()) , "symbol": stock, "dir": "SELL", "price": sell_at-1, "size": 15})

# Main
def main():
    exchange = connect()
    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)

    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    while(True):
        bond(exchange)
        pennying(exchange, "BABA")
        pennying(exchange, "BABZ")

if __name__ == "__main__":
    main()
    
