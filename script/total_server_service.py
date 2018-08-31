# coding: utf-8

import socket
import socketserver
import struct
import json
import os
import sys

socket.setdefaulttimeout(20)
# global variable, key is task name, value is map({address: state})
_address = {}

# global variable, list is task name
_task = []

# global variable, key is task name, value is map{'filename': number}
_result = {}

# global variable, key is task name, value is filename
_matrix = {}


# split matrix and return matrix of split finish
def split_matrix(task):
    if _matrix[task]:
        filename = _matrix[task][0]
        with open('./data/' + filename, 'r') as f_read:
            matrix_init = json.load(f_read)
            matrix_finish = matrix_init
            if filename in _result[task]:
                matrix_finish = matrix_init[_result[task] + 1:]
        return filename, matrix_finish
    else:
        print('success: All matrix is finish and result in the ./result!')
        sys.exit(0)


class TotalSocketServer(socketserver.BaseRequestHandler):

    # send matrix to client
    def send_matrix(self, task):
        filename, matrix_finish = split_matrix(task)
        send_file_message = json.dumps(matrix_finish).encode()
        headers = {
            'task': task,
            'size': len(send_file_message),
            'filename': filename,
            'action': "compute",
        }
        headers_json = json.dumps(headers).encode()
        headers_pack = struct.pack('i', len(headers_json))
        self.request.send(headers_pack)
        self.request.send(headers_json)
        self.request.sendall(send_file_message)

    def handle(self):
        response = 'Error: suffer a unknown problem! '
        address = self.client_address
        receive = self.request.recv(4)
        headers_pack = self.request.recv(struct.unpack('i', receive)[0])
        headers = json.loads(headers_pack.decode())
        task = headers['task']
        action = headers['action']

        # receive task deploy and add task to all environment, task is recode all task, address is all
        # task exec address, {'address': state}, result
        if task not in _task and action == 'task':
            _task.append(task)
            _address[task] = {}
            _matrix[task] = []
            os.mkdir('./data/%s' % task)
            response = 'access'

        if task in _task and action == 'delete':
            _task.remove(task)
            _address.pop(task)
            _matrix.pop(task)
            os.removedirs('./data/%s' % task)
            response = 'delete'

        if task in _task and action == 'storage':
            filename = headers['filename']
            files = json.loads(self.request.recv(headers['size']).decode())
            with open('./data/%s' % filename, 'w') as f_write:
                json.dump(files, f_write)
            _matrix[task].append(filename)
            response = 'storage'

        # receive client exec task request
        if task in _task and action == 'request':
            _address[task].append({address: 'work'})
            # send matrix to client
            self.send_matrix(task)

        # receive result of client, maybe have some data is not finish, we'll need send those data to other client.
        if task in _task and action == 'result':
            filename = headers['filename']
            number = headers['number']
            result_matrix = json.loads(self.request.recv(headers['size']).decode())
            _result[task][filename] = number
            with open('./data/' + filename, 'r') as f_read:
                matrix = json.load(f_read)
                if len(matrix) == number:
                    _address[task][address] = 'free'
                    _matrix[task].pop(filename)
                    if _matrix[task]:
                        self.send_matrix(task)
                    else:
                        print('success: All matrix is finish and result in the ./result!')
                        sys.exit(0)
                else:
                    _address[task].pop(address)
            with open('./result/' + filename, 'w') as f_write:
                json.dump(result_matrix, f_write)

        self.request.sendall(response.encode())
        self.request.close()


def run():
    total_server = socketserver.TCPServer(('0.0.0.0', 17788), TotalSocketServer)
    total_server.serve_forever()
