# scratch space for working on this piece of code in the python REPL interpreter

import socket
import ssl
import binascii
from importlib import reload # --> ssock.reload(ssock) is super-handy

hostname = '1.1.1.1'
port = 853

# secure context wrapped tcp socket ready for writing
def connectsend(query):
    # set default/secure context
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('/etc/ssl/cert.pem')

    # create a socket and wrap it
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    wrsock = context.wrap_socket(sock, server_hostname=hostname)
    wrsock.connect((hostname, port))

    # pad and encode and send and receive 
    wrsock.send(binascii.hexlify(padencode(query)))
    data = wrsock.recv(1024)
    print(data)
    return data

# format query with two-byte length prefix per RFC1035
def padencode(query):
  return str.encode("\x00" + chr(len(query)) + query)
