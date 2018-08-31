# coding: utf-8

import optparse
import json
import sys
import socket
import struct
import os
import hashlib
from datetime import datetime

# set socket timeout
socket.setdefaulttimeout(10)

# set option of the script
_parser = optparse.OptionParser()
_parser.add_option('-n', '--name', action='store', dest='name',
                   help='you must offer a task name in the option')
_parser.add_option('-a', '--address', action='store', dest='address',
                   help='you must offer a client address in the option')

# define global variable
server_address = ('0.0.0.0', 17788)
_variable = {}
task_name = None


# parse parameter of user enter
def parse_option():
    try:
        (options, args) = _parser.parse_args()
        name = options.name
        client_address = options.address
        if not name or not client_address:
            raise optparse.OptionConflictError('', '')
        _variable['task'] = name
        _variable['address_file'] = client_address

    except optparse.OptionConflictError:
        _parser.print_help()


# generate md5 of specify message
def md5(message):
    sha = hashlib.sha256()
    sha.update(message)
    return sha.hexdigest()


def send_socket(address, message1, message2):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)
    client.send(message1)
    client.sendall(message2)
    if client.recv(6).decode() == 'access':
        if address == server_address:
            send_file()
        else:
            send_compute_matrix(address)
    else:
        print('your task is rejected, please check it and try\'in again!')
    client.close()


# send all file to total.
def send_file():
    path = input('Enter your matrix path:')
    if not os.path.isdir(path):
        print('Error: your path is invalid!')
        headers = {
            'task': task_name,
            'action': 'delete',
        }
        headers_json = json.dumps(headers).encode()
        headers_pack = struct.pack('i', len(headers_json))
        send_socket(server_address, headers_pack, headers_json)
        sys.exit(1)

    all_file = os.listdir(path)
    for file in all_file:
        with open(file, 'r') as f_read:
            file_json = json.dumps(json.load(f_read)).encode()
            headers = {
                'task': task_name,
                'filename': os.path.basename(file),
                'size': len(file_json),
                'action': 'storage',
            }
            headers_json = json.dumps(headers).encode()
            headers_pack = struct.pack('i', len(headers_json))
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(server_address)
            client.send(headers_pack)
            client.send(headers_json)
            client.sendall(file_json)
            client.close()


# send compute matrix to client
def send_compute_matrix(address):
    file_matrix = input('Enter your compute matrix path:')
    if not os.path.isfile(file_matrix):
        print('Error: your path is invalid!')
        headers = {
            'task': task_name,
            'action': 'delete',
        }
        headers_json = json.dumps(headers).encode()
        headers_pack = struct.pack('i', len(headers_json))
        send_socket(server_address, headers_pack, headers_json)

        headers = {
            'task': task_name,
            'filename': os.path.basename(file_matrix),
            'action': 'delete',
        }
        headers_json = json.dumps(headers).encode()
        headers_pack = struct.pack('i', len(headers_json))
        send_socket(address, headers_pack, headers_json)

        sys.exit(1)

    with open(file_matrix, 'r') as f_read:
        file_json = json.dumps(json.load(f_read)).encode()
        headers = {
            'task': task_name,
            'filename': os.path.basename(file_matrix),
            'size': len(file_json),
            'action': 'storage',
        }
        headers_json = json.dumps(headers).encode()
        headers_pack = struct.pack('i', len(headers_json))
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(address)
        client.send(headers_pack)
        client.send(headers_json)
        client.sendall(file_json)
        client.close()


# send task name and matrix file to total socket server
def send_total_socket():
    send_file_md5 = md5(str(datetime.now()).encode())
    global task_name
    task_name = _variable['task'] + send_file_md5
    headers = {
        'task': task_name,
        'action': 'task',
    }
    headers_json = json.dumps(headers).encode()
    headers_pack = struct.pack('i', len(headers_json))
    send_socket(server_address, headers_pack, headers_json)


# send task name to all client
def send_client_socket():
    headers = {
        'task': task_name,
        'action': 'deploy',
    }
    headers_json = json.dumps(headers).encode()
    headers_pack = struct.pack('i', len(headers_json))
    for address in _variable['address_file']:
        send_socket(address, headers_pack, headers_json)


if __name__ == '__main__':
    parse_option()
    send_total_socket()
    send_client_socket()
