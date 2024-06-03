import logging
import threading
import socket
import json
import os
import argparse
from dotenv import load_dotenv
from aifc import Error
import shutil
from pathlib import Path

load_dotenv()

HOST = os.getenv("RHOST")
PORT = int(os.getenv("RPORT"))
MAX_THREADS = 5
QUARANTINE_PATH = Path(".")

logging.basicConfig(format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level = logging.INFO)
logger = logging.getLogger(__name__)

def CheckLocalFile_func(request_data): # Check Handler
    try:
        f = open(request_data['params']['param1'], 'rb')
        data = f.read()
        f.close()
        start = 0
        index = []

        while True: # Repeat until all occurrences are found
            tmp = data[start::].find(bytes.fromhex(request_data['params']['param2']))
            start += tmp + 1
            index.append(start - 1)
            if tmp == -1:
                break

        if index[0] != -1: # There are no occurrences
            response_data = {"status": "* Success",
                             "data": f"\t- The {request_data['params']['param2']} signature in the local {request_data['params']['param1']} file starts with {index[:-1]} byte(s)"}
        else: # There are occurrences
            response_data = {"status": "* Success",
                             "data": f"\t- The {request_data['params']['param2']} signature is missing from the local {request_data['params']['param1']} file"}
        logging.debug(f'+ CheckLocalFile succeed')
    except Exception as e: # Exception Handler
        logging.error(e)
        response_data = {"status": "* Failure",
                         "data": f"\t- {e}"}
    return response_data

def QuarantineLocalFile_func(request_data): # Quarantine Handler
    try:
        shutil.move(Path(request_data["params"]["param1"]), QUARANTINE_PATH)
        response_data = {"status": "* Success",
                             "data": f"\t- The {request_data['params']['param1']} file has been moved to quarantine"}
        logging.warning(f'+ The {request_data["params"]["param1"]} file has been moved to {QUARANTINE_PATH} quarantine')
    except Exception as e: # Exception Handler
        logging.error(e)
        response_data = {"status": "* Failure",
                         "data": f"\t- {e}"}
    return response_data

def handle_client(client_socket, semaphore, addr):
    semaphore.acquire() # Occupying the semaphore
    logging.info(f'+ Connection from {addr} is active')
    try:
        request = client_socket.recv(2048)
        if not request:
            return
        request_data = json.loads(request) # Getting JSON data
        logging.debug(f'+ Request from {addr} received')
        if request_data['command'] == 'CheckLocalFile':
            response_data = CheckLocalFile_func(request_data)
        elif request_data['command'] == 'QuarantineLocalFile':
            response_data = QuarantineLocalFile_func(request_data)
        else:
            response_data = {"status": "* Failure",
                             "data": f"\t- The wrong command was specified"}
        response = json.dumps(response_data)
        client_socket.sendall(response.encode()) # Sending JSON data
        logging.debug(f'+ Reply for {addr} sent')
    except Exception as e: # Exception Handler
        logging.error(e)
    finally:
        semaphore.release() # Releasing the semaphore
    client_socket.close()
    logging.info(f'+ Connection from {addr} is closed')

def main():
    global QUARANTINE_PATH
    parser = argparse.ArgumentParser(description = 'Start a multithreaded TCP server.') # Argument handlers
    parser.add_argument('--max-threads',
                        type = int,
                        default = 5,
                        help = 'maximum number of threads to use (default: 5)')
    parser.add_argument('--quarantine-folder',
                        type = str,
                        default = '.',
                        help = 'quarantine folder (default: ./)')
    args = parser.parse_args()

    MAX_THREADS = args.max_threads
    QUARANTINE_PATH = Path(args.quarantine_folder)

    logging.debug(f'+ Maximum number of threads is {MAX_THREADS}')
    logging.debug(f'+ Quarantine folder is {QUARANTINE_PATH}')

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT)) # Port's bind
    logging.debug('+ Bind succeed')
    server_socket.listen()
    logging.info(f'+ Server is listening on {HOST}:{PORT}')

    semaphore = threading.Semaphore(MAX_THREADS) # Creating a semaphore
    while True:
        client_socket, addr = server_socket.accept() # Accept a new connection
        logging.info(f'+ New connection from {addr}')
        client_thread = threading.Thread(target = handle_client, args = (client_socket, semaphore, addr)) # New thread
        client_thread.start()

if __name__ == "__main__":
    main()