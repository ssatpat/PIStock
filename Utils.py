import json
import time
import datetime
import platform
import socket
import gzip
import random # Used to generate sample data; comment out this line if real data is used
import requests
from iexfinance.stocks import Stock
import config as c

if not c.VERIFY_SSL:
    requests.packages.urllib3.disable_warnings()

myDict = {}

def send_data():
    global myDict
    # Send OMF to relay
    get_data()
    for symbol in c.tickr:
        for p_type in c.point_types:
            point_name = symbol + "." + p_type
            data = {
                'value': myDict[symbol][p_type],
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
            }
            write_to_relay(point_name, data)
            print 'Sent ', point_name

        for stream in c.OCSStreams:
            data = {
                'TimeStamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'Name': symbol,
                'Price': myDict[symbol]['price'],
                'Volume': myDict[symbol]['volume'],
                'Open': myDict[symbol]['open'],
                'Close': myDict[symbol]['close']
            }
            write_to_ocs(stream, data)
            print 'Sent ', stream
        
        time.sleep(1)
        
def get_data():
    batch = Stock(c.tickr)
    current = batch.get_price()
    price = batch.get_price()
    volume = batch.get_volume()
    open = batch.get_open()
    close = batch.get_close()

    global myDict
    myDict = {}
    for symbol in c.tickr:
        myDict[symbol] = {"price": price[symbol],
                            "volume": volume[symbol],
                            "open": open[symbol],
                            "close": close[symbol]
                            }

def write_to_relay(pointName, data):
    data_body = [{
      "containerid": pointName,
      "values": [{
        "timestamp": data['timestamp'],
        "value": data['value']
        }]
    }]
    send_omf_message_to_endpoint("data", data_body, c.PRODUCER_TOKEN, c.INGRESS_URL)


def write_to_ocs(pointName, data):
    data_body = [{
      "containerid": pointName,
      "values": [{
        "TimeStamp": data['TimeStamp'],
        "Name": data['Name'],
        "Price": data['Price'],
        "Volume": data['Volume'],
        "Open": data['Open'],
        "Close": data['Close']
        }]
    }]
    send_omf_message_to_endpoint("data", data_body, c.OCS_PRODUCER_TOKEN, c.OCS_INGRESS_URL)

def send_omf_message_to_endpoint(message_type, message_omf_json, token, url):
    try:
        # Compress json omf payload, if specified
        compression = 'none'
        if c.USE_COMPRESSION:
            msg_body = gzip.compress(bytes(json.dumps(message_omf_json), 'utf-8'))
            compression = 'gzip'
        else:
            msg_body = json.dumps(message_omf_json)
        # Assemble headers
        msg_headers = {
            'producertoken': token,
            'messagetype': message_type,
            'action': 'create',
            'messageformat': 'JSON',
            'omfversion': '1.0',
            'compression': compression
        }

        # Send the request, and collect the response
        response = requests.post(
            url,
            headers=msg_headers,
            data=msg_body,
            verify=c.VERIFY_SSL,
            timeout=c.WEB_REQUEST_TIMEOUT_SECONDS
        )
        # Print a debug message, if desired; note: you should receive a
        # response code 204 if the request was successful!
        print('Response from relay from the initial "{0}" message: {1} {2}'.format(message_type, response.status_code,
                                                                                   response.text))

    except Exception as e:
        # Log any error, if it occurs
        print("An error ocurred during web request: " + str(e))

