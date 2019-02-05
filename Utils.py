import json
import time
import datetime
import platform
import socket
import gzip
import random # Used to generate sample data; comment out this line if real data is used
import requests
from iexfinance.stocks import Stock


tickr = ['AAPL', 'TWTR', 'TSLA', 'NFLX', 'BABA', 'MSFT', 'DIS', 'GE', 'FIT', 'F']
point_types = ['price', 'open', 'close', 'volume']  

PRODUCER_TOKEN = "uid=dc75d259-28b1-4085-bcb2-c63a91464192&crt=20181018172015100&sig=lBjuU1EwJQeMisu9BIIxPFnMap5s2h0CmadoN2SYfpU="

INGRESS_URL = "https://ssatpathyrelay.dev.osisoft.int:5460/ingress/messages"

USE_COMPRESSION = False

WEB_REQUEST_TIMEOUT_SECONDS = 30

VERIFY_SSL = False
if not VERIFY_SSL:
    requests.packages.urllib3.disable_warnings()

myDict = {}

def sendData():
    global myDict
    # Send OMF to relay
    getData()
    print myDict
    for symbol in tickr:
        for p_type in point_types:
            point_name = symbol + "." + p_type
            data = {
                'value': myDict[symbol][p_type],
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
            }
            print point_name
            write_to_relay(point_name, data)
            print 'Sent ', point_name
        
        time.sleep(1)
        
def getData():
    batch = Stock(tickr)
    current = batch.get_price()
    price = batch.get_price()
    volume = batch.get_volume()
    open = batch.get_open()
    close = batch.get_close()

    global myDict
    myDict = {}
    for symbol in tickr:
        myDict[symbol] = {"price": price[symbol],
                            "volume": volume[symbol],
                            "open": open[symbol],
                            "close": close[symbol]
                            }
    print myDict


def write_to_relay(pointName, data):
    data_body = [{
      "containerid": pointName,
      "values": [{
        "timestamp": data['timestamp'],
        "value": data['value']
        }]
    }]
    send_omf_message_to_relay_endpoint("data", data_body)


def send_omf_message_to_relay_endpoint(message_type, message_omf_json):
    try:
        # Compress json omf payload, if specified
        compression = 'none'
        if USE_COMPRESSION:
            msg_body = gzip.compress(bytes(json.dumps(message_omf_json), 'utf-8'))
            compression = 'gzip'
        else:
            msg_body = json.dumps(message_omf_json)
        # Assemble headers
        msg_headers = {
            'producertoken': PRODUCER_TOKEN,
            'messagetype': message_type,
            'action': 'create',
            'messageformat': 'JSON',
            'omfversion': '1.0',
            'compression': compression
        }

        # Send the request, and collect the response
        response = requests.post(
            INGRESS_URL,
            headers=msg_headers,
            data=msg_body,
            verify=VERIFY_SSL,
            timeout=WEB_REQUEST_TIMEOUT_SECONDS
        )
        # Print a debug message, if desired; note: you should receive a
        # response code 204 if the request was successful!
        print('Response from relay from the initial "{0}" message: {1} {2}'.format(message_type, response.status_code,
                                                                                   response.text))

    except Exception as e:
        # Log any error, if it occurs
        print("An error ocurred during web request: " + str(e))

