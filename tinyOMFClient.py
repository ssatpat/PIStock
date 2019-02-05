import json
import time
import datetime
import platform
import socket
import gzip
import requests
import Utils as u

print 'Sending OMF data...'

while True:
    u.send_data()