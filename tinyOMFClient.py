import json
import time
import datetime
import platform
import socket
import gzip
import requests
import dataWriter as dw

point = 'myFavoritePIpoint'
points = ['...', '....']
print 'Sending OMF data...'

# myDict = {
#     "tickr" : {
#         "price" : price,
#         "volume": volume,
#         "open": Open,
#         "close": close,
#     }
# }

while True:
    # Send OMF to relay
    for symbol in tickr:
        for point in points:
            data = {
                'value': random.random(),
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z'
            }
            dw.write_to_relay(point, data)
            print 'Sent ', symbol
            time.sleep(1)
        
        # Send OMF to OCS
        # ... 

