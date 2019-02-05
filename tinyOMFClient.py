import json
import time
import datetime
import platform
import socket
import gzip
import requests
import Utils as u

print 'Setting up PI points...'
# Uncomment to create new PI points
#u.create_pi_points()

print 'Sending OMF data...'
while True:
    u.send_data()