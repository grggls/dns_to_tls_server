# dnstotls_server.py

import socket, sys, subprocess
import logging
import argparse
import validators

def dnstotls(port, maxconn):
    # create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind to port
    server_address = ('0.0.0.0', port)
    logging.warning('starting up %s on %s port = %s maxconns = %s', sys.argv[0], *server_address, maxconn)
    sock.bind(server_address)

    # listen for maximum three incoming connections
    sock.listen(maxconn)

    while True:
        # Wait for a connection
        connection, client_address = sock.accept()
        try:
            # receive query from the user, validate, transmit it to cloudflare
            while True:
                data = connection.recv(16)
                if not data: logging.warning('no data from', client_address); break
                query = data.strip().decode('utf-8')
                logging.warning('query received for %s', query)
                if not validators.domain(query): logging.warning('invalid url {} from {}'.format(query, client_address)); break
                result = resolve_with_doh(query); logging.info(result)
                connection.sendall(result.encode())
                logging.warning('response sent to %s: %s', client_address, query)

        # promise to clean up the connection
        finally:
            connection.close()

def resolve_with_doh(query):
    return subprocess.run(['doh', query], stdout=subprocess.PIPE).stdout.decode('utf-8')

# call main()
if __name__ == "__main__":
    # set up logging
    logging.basicConfig(format='%(asctime)s %(message)s')

    # parse command line maximum connections
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", action="store", type=int, default=1053, help="listening port for incoming DNS queries")
    parser.add_argument("-c", "--connections", action="store", type=int, default=1, help="maximum concurrent connections to the service")
    args = parser.parse_args()

    # runit
    dnstotls(args.port, args.connections)
