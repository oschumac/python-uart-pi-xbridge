#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Make https POST request using sockets.
NOTE: it doesn't try to validate server certificate if cacert.pem is
not present
http://stackoverflow.com/q/9303419
"""
import os
import shutil
import socket
import sys
import ssl

from contextlib import closing

try: from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode # Python 3

hostname = "larsaps.azurewebsites.net"
data = urlencode(dict(email='john', password='example…')).encode('ascii')


data = {
	"enterdBy": 'OpenAPS Controller',
	"eventType": 'APS_TEMP',
	"glucose": 100, 
	"glucoseType": 'fake',
	"insulin": 0.5, 
	"notes": 'BZ: 12345678	',
	"units": 'mg/dl',
	"created_at" : '123456787866' }



# enable validation of server certificate against given CAs
#NOTE: it does nothing if server doesn't provide a certificate
ca_certs = 'cacert.pem' # http://curl.haxx.se/ca/cacert.pem
kwargs = {}
if os.path.exists(ca_certs):
    kwargs.update(cert_reqs=ssl.CERT_REQUIRED,
                  ssl_version=ssl.PROTOCOL_SSLv3,
                  ca_certs=ca_certs)

# make https POST request
with closing(ssl.wrap_socket(socket.socket(), **kwargs)) as s:
    s.connect((hostname, 443)) # connect
    s.sendall("POST HTTP/1.1\r\n" # send headers
              "Host: {hostname}\r\n"
              "Connection: close\r\n"
              "Content-Type : application/json charset=utf-8 \r\n"
              "Content-Length: {len}\r\n"
              "\r\n".format(hostname=hostname, len=len(data)).encode('ascii'))
    s.sendall(json.dumps(data)) # send data
    with closing(s.makefile()) as f: # read response
        shutil.copyfileobj(f, sys.stdout) #XXX encoding
	