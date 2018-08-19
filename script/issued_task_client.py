# coding: utf-8

import optparse
import json
import sys
import socket
import struct
import hashlib

# set socket timeout
socket.setdefaulttimeout(10)

# set option of the script
_parser = optparse.OptionParser()
_parser.add_option('-f', '--file', action='store', dest='file',
                   help='you must offer a json file path to store the matrix')
_parser.add_option('-n', '--name', action='store', dest='name',
                   help='you must offer a task name in the option')
_parser.add_option('-a', '--address', action='store', dest='address',
                   help='you must offer a json file path to store the client address')

# define global variable
server_address = ('0.0.0.0', 17788)
_variable = {}


# parse parameter of user enter
def parse_option():
    try:
        (options, args) = _parser.parse_args()
        file = options.file
        name = options.name
        address = options.address
        if not file or not name or not address:
            raise optparse.OptionConflictError('', '')
        _variable['matrix_file'] = json.load(file)
        _variable['address_file'] = json.load(address)
        _variable['task'] = name

    except optparse.OptionConflictError:
        _parser.print_help()
    except json.JSONDecodeError:
        print('Error, you must offer valid json file path', sys.stderr)


# generate md5 of specify message
def md5(message):
    sha = hashlib.sha256()
    sha.update(message)
    return sha.hexdigest()


# send message to address, the address is tuple (ip, port)
def socket_client(address, message1, message2, message3):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)
    client.send(message1)
    client.send(message2)
    client.sendall(message3)
    client.close()


# send task name and matrix file to total socket server
def send_total_socket():
    send_file_message = json.dumps(_variable['matrix_file']).encode()
    send_file_md5 = md5(send_file_message)
    headers = {
        'task': _variable['task'] + send_file_md5,
        'size': len(send_file_message),
        'md5': send_file_md5,
    }
    headers_json = json.dumps(headers).encode()
    headers_pack = struct.pack('i', len(headers_json))
    socket_client(server_address, headers_pack, headers_json, send_file_message)


# send task name to all client
def send_client_socket():
    send_file_message = json.dumps(_variable['matrix_file']).encode()
    send_file_md5 = md5(send_file_message)
    headers = {
        'task': _variable['task'] + send_file_md5,
        'size': 1,
        'md5': send_file_md5,
    }
    headers_json = json.dumps(headers).encode()
    headers_pack = struct.pack('i', len(headers_json))
    for address in _variable['address_file']:
        socket_client(address, headers_pack, headers, '1')


if __name__ == '__main__':
    print(md5('777'.encode()))
    # parse_option()
    # send_total_socket()
    # send_client_socket()
