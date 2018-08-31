# coding: utf-8

import socketserver
import struct
import json
import socket
from script.matrix_multiplication_script import MatrixDeal
import os
import sys

# task is list, and storage all task name
# global variable, key is task name, value is multiplication matrix.
_task = []
# storage result with map{'matrix':xx, 'number': number}
_result = {'matrix': [], 'number': 0}
compute_matrix = None
task_name = None
file_name = None
server_address = ('0.0.0.0', 17788)


# send result to total, the result maybe is complete, maybe is partial.
def response_total(matrix):
    m_deal = MatrixDeal(matrix, compute_matrix, _result)
    # if matrix is not true. send error to total.
    if not m_deal.judge_matrix():
        sys.exit(0)
    m_deal.multiply_matrix_process()
    send_total_result()


# send result to total
def send_total_result():
    send_file_message = json.dumps(_result['matrix']).encode()
    headers = {
        'task': task_name,
        'size': len(send_file_message),
        'filename': file_name,
        'number': _result['number'],
        'action': 'result',
    }
    headers_json = json.dumps(headers).encode()
    headers_pack = struct.pack('i', len(headers_json))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_address)
    client.send(headers_pack)
    client.send(headers_json)
    client.sendall(send_file_message)
    client.close()


def send_socket(address, message1, message2):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)
    client.send(message1)
    client.sendall(message2)
    if client.recv(6).decode() == 'access':
        pass
    else:
        print('your task is rejected, please check it and try\'in again!')
    client.close()


def request_total():
        headers = {
            'task': task_name,
            'action': 'request',
        }
        headers_json = json.dumps(headers).encode()
        headers_pack = struct.pack('i', len(headers_json))
        send_socket(server_address, headers_pack, headers_json)


class TotalSocketServer(socketserver.BaseRequestHandler):

    def handle(self):
        response = 'Error: suffer a unknown problem! '
        receive = self.request.recv(4).decode()
        headers_pack = self.request.recv(struct.unpack('i', receive)[0])
        headers = json.loads(headers_pack.decode())
        task = headers['task']
        action = headers['action']

        # receive task deploy
        if task not in _task and action == 'deploy':
            _task.append(task)
            global task_name
            task_name = task
            response = 'access'

        if task in _task and action == 'storage':
            filename = headers['filename']
            files = json.loads(self.request.recv(headers['size']).decode())
            with open('./matrix/%s' % filename, 'w') as f_write:
                json.dump(files, f_write)
            global compute_matrix
            compute_matrix = './matrix/%s' % filename
            request_total()
            response = 'storage'

        if task in _task and action == 'delete':
            filename = headers['filename']
            os.remove(filename)
            global compute_matrix
            compute_matrix = None
            global task_name
            task_name = None
            response = 'delete'

        if task in _task and action == 'compute':
            matrix = json.loads(self.request.recv(headers['size']).decode())
            global file_name
            file_name = headers['filename']
            response_total(matrix)
            response = 'compute'

        if action == 'quit':
                send_total_result()
                sys.exit(0)

        if action == 'finish':
            sys.exit(0)

        self.request.sendall(response.encode())
        self.request.close()


def run():

    total_server = socketserver.TCPServer(('0.0.0.0', 17778), TotalSocketServer)
    total_server.serve_forever()
