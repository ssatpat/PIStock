import json
import time
import datetime
import platform
import socket
import gzip
import random # Used to generate sample data; comment out this line if real data is used
import requests

PRODUCER_TOKEN = "uid=dc75d259-28b1-4085-bcb2-c63a91464192&crt=20181018172015100&sig=lBjuU1EwJQeMisu9BIIxPFnMap5s2h0CmadoN2SYfpU="

INGRESS_URL = "https://ssatpathyrelay.dev.osisoft.int:5460/ingress/messages"

USE_COMPRESSION = False

WEB_REQUEST_TIMEOUT_SECONDS = 30

VERIFY_SSL = False

def write_to_relay(pointName, data):
    data = {
        'value': random.random(),
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
    }
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

