# dnstotls_server.py

import socket, sys, subprocess
import logging
import argparse
import validators

def dnstotls(port, maxconn, stub):
    # create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind to port
    server_address = ('0.0.0.0', port)
    logging.warning('starting up %s on %s {port: %s, maxconns: %s, resolver: %s}', sys.argv[0], *server_address, maxconn, stub)
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

                try:
                    query = data.strip().decode('utf-8')
                except UnicodeDecodeError:
                    logging.warning('non-unicode byte detected (keyboard interrupt perhaps?)'); break

                logging.warning('query received for %s', query)
                if not validators.domain(query): logging.warning('invalid url {} from {}'.format(query, client_address)); break

                # choose your resolver
                if stub == 'doh':
                  result = resolve_with_doh(query); logging.info(result)
                elif stub == 'curl':
                  result = resolve_with_curl(query); logging.info(result)
                elif stub == 'kdig':
                  result = resolve_with_kdig(query); logging.info(result)
                else:
                  logging.error('invalid stub resolver configured')

                connection.sendall(result.encode())
                logging.warning('response sent to %s: %s', client_address, query)

        # promise to clean up the connection
        finally:
            connection.close()

def resolve_with_doh(query):
    command = 'doh {}'.format(query)
    return run_stub_command(command)

def resolve_with_curl(query):
    url = 'https://cloudflare-dns.com/dns-query?name={}'.format(query)
    command = 'curl --silent -H "accept: application/dns-json" "{}"'.format(url)
    return run_stub_command(command)

def resolve_with_kdig(query):
    command = 'kdig -d @1.1.1.1 +tls-ca +tls-host=cloudflare-dns.com {}'.format(query)
    return run_stub_command(command)

def run_stub_command(command):
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode('utf-8')

# call main()
if __name__ == "__main__":
    # set up logging
    logging.basicConfig(format='%(asctime)s %(message)s')

    # parse command line maximum connections
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-p", "--port", action="store", type=int, default=1053, help="listening port for incoming DNS queries")
    parser.add_argument("-c", "--connections", action="store", type=int, default=1, help="maximum concurrent connections to the service")
    parser.add_argument("-s", "--stub", action="store", type=str, default="doh", choices=["doh", "curl", "kdig"], help="choose which stub resolver to use", const="doh", nargs="?")
    args = parser.parse_args()

    # runit
    dnstotls(args.port, args.connections, args.stub)
