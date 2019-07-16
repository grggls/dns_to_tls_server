import socket
import ssl
import dns
import binascii
from importlib import reload # --> ssock.reload(ssock) is super-handy
import logging

hostname = '1.1.1.1'
port = 853

# secure context wrapped tcp socket ready for writing
def connectsend(query):
  context = context()
  socket = socket(context)
  

def context():
    # set default/secure context
    context = ssl.create_default_context()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('/etc/ssl/cert.pem')
    return context

def socket(context):
    # create a socket and wrap it
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    wrsock = context.wrap_socket(sock, server_hostname=hostname)
    wrsock.connect((hostname, port))
    cfcert = wrsock.getpeercert()

    # pad and encode and send and receive 
    # wrsock.send(padencode(query))
    # data = wrsock.recv(4096)
    # print(data)
    # return data
    return wrsock

# format query with two-byte length prefix per RFC1035
def padencode(domain):
    import dns.message as message
    msg = message.make_query(domain, 'A') 
    return binascii.hexlify(msg.to_text().encode())
