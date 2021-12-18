import websocket, json, numpy,  pprint, tablib, numpy
import config
from binance.enums import *
from binance.client import Client

RSI_PERIOD = 14
OVERSOLD_THRESHOLD = 30
OVERBOUGHT_THRESHOLD = 70
TRADE_QUANTITY =0.05
TRADE_SYMBOL = 'ETHUSD'
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

closes = []
in_position = False
client = Client(config.API_KEY, config.API_SECRET, tld ='us')

def order(quantity, symbol, side, order_type=ORDER_TYPE_MARKET):
	try:
		order = client.create_order(symbol = symbol,side = side,type=order_type,quantity=quantity)
		print("sending order")
		print(order)
	except Exception as e:
		return False
	return True   


def on_open(ws):
	print('opened connection')

def on_close(ws):
	print("closed connection")

def on_message(ws, message):
	print('received message')
	json_message = json.loads(message)
	pprint.pprint(json_message)

	candle = message['k']
	is_candle_closed = candle['x']
	close = candle['c']

	if is_candle_closed:
		print("candle closed at {}".format(close))
		closes.append(float(close))
		print("closes")
		print(closes)

		if len(closes) > RSI_PERIOD:
			np_closes = numpy.array(closes)
			rsi = tablib.RSI(np_closes, RSI_PERIOD)
			print("all rsis calculated so far")
			print(rsi)
			last_rsi = rsi[-1]
			print("the current rsi is {}".format(last_rsi))

			if last_rsi > OVERBOUGHT_THRESHOLD:
				if in_position:
					print("Overbought, Sell! Sell!Sell!")
					order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
					if order_succeeded:
						in_position = False
				else:
					print("It is overbought, but we don't own any. Nothing to do.")


			if last_rsi <OVERSOLD_THRESHOLD:
				if in_position:
					print("It is oversold, but you already own it, nothing to do.")
				else:
					print("Oversold! Buy! Buy! Buy!")
					# put binance order logic here
					order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
					if order_succeeded:
						in_position= True 



ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_message=on_message, on_close=on_close)
ws.run_forever()
