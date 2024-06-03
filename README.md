# PT_START_SANDBOX
This project implements a multithreaded TCP server and a single-threaded console client for sending requests to the server. Requests are transmitted in JSON format and processed by the server according to the specified command.

## Commands
The server supports two commands:

- `CheckLocalFile` - check the specified file in the request for a signature. The file path and signature are transmitted in the request parameters. The server returns a list of offsets of the found signatures in the response. The signature is represented as a set of bytes up to 1KB in length.
- `QuarantineLocalFile` - move the specified file to quarantine (to a special directory specified in the server startup options).

## Server Startup
The following options are specified when the server is started:

- `--max-threads` - the number of threads in the request processing pool (default 5).
- `--quarantine-folder` - the path to the quarantine directory (default ./).

Example of starting the server:

```python3 server.py --max-threads 10 --quarantine-folder /path/to/quarantine```

## Client Startup
The following options are specified when the client is started:

flags for `CheckLocalFile`:
- `--path` - the path to the file to be checked.
- `--sign` - the signature in hexadecimal format to be found in the checked file.

flag for `QuarantineLocalFile`:
- `--path` - the path to the file to be quarantined.

Examples of starting the client:

```python3 client.py CheckLocalFile --path /path/to/file --sign 54a1```

```python3 client.py QuarantineLocalFile --path /path/to/file```

##Termination
The application terminates execution when the user interrupts it with the SIGINT signal (Ctrl+C).

##Implementation Language
The project is implemented in Python 3 and is compatible with both POSIX and Windows systems.

