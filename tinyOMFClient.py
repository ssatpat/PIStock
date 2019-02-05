import json
import time
import datetime
import platform
import socket
import gzip
import requests
import Utils as u

# myDict = {
#     "tickr" : {
#         "price" : price,
#         "volume": volume,
#         "open": Open,
#         "close": close,
#     }
# }
print 'Sending OMF data...'

while True:
    u.sendData()


