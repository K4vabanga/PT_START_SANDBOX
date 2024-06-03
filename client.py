import socket
import json
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv("RHOST")
PORT = int(os.getenv("RPORT"))

def check(args): # Data for check
    return {'command': "CheckLocalFile", 'params': {'param1': args.path, 'param2': args.sign}}

def quarantine(args): # Data for quarantine
    return {'command': "QuarantineLocalFile", 'params': {'param1': args.path}}

def main():
    parser = argparse.ArgumentParser(description = 'Start a client.') # Argument handlers
    subparsers = parser.add_subparsers(title = 'subcommands',
                                       description = 'valid subcommands',
                                       help = 'description')
    check_parser = subparsers.add_parser('CheckLocalFile',
                                         help = 'Check the local file for a signature')
    check_parser.add_argument('--path',
                              type = str,
                              help = 'path to the file being checked',
                              required = True)
    check_parser.add_argument('--sign',
                              type = str,
                              help = 'the signature being checked',
                              required = True)
    check_parser.set_defaults(func = check)

    quarantine_parser = subparsers.add_parser('QuarantineLocalFile',
                                              help = 'Send the file to quarantine')
    quarantine_parser.add_argument('--path',
                                   type = str,
                                   help = 'the path to the file to be quarantined',
                                   required = True)
    quarantine_parser.set_defaults(func = quarantine)
    args = parser.parse_args()

    if not vars(args):
        print('* This is a client for checking a file on the server for signatures and sending files to quarantine.\n* ',end='')
        parser.print_usage()
    else:
        request_data = args.func(args) # Generate JSON data

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT)) # Create a new connection
        request = json.dumps(request_data)
        client_socket.sendall(request.encode()) # Sending JSON data

        response = client_socket.recv(2048)
        response_data = json.loads(response) # Getting JSON data
        print(response_data['status'],'\n',response_data['data'])
        client_socket.close()

if __name__ == "__main__":
    main()
