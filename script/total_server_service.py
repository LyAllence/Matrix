# coding: utf-8

import socketserver
import struct
import json
import hashlib

# global variable, key is task name, value is list, and there are address in list
_address = {}

# global variable, key is task name, value is task result
_task = {}

# global variable, key is task name, value is result
_result = {}


# generate md5 of specify message
def md5(message):
    sha = hashlib.sha256()
    sha.update(message)
    return sha.hexdigest()


class TotalSocketServer(socketserver.BaseRequestHandler):

    def handle(self):
        address = self.client_address
        receive = self.request.recv(4)
        headers_pack = struct.unpack('i', receive)[0]
        headers = json.loads(headers_pack.decode())
        size = headers['size']
        md51 = headers['md5']
        task = headers['task']
        task_file = self.request.recv(size)

        # receive file is invalid!
        if md5(task_file) != md51:
            self.request.send('fail: md5 error')
            return

        # receive task deploy
        if task not in _task and size > 1:
            _task[task] = task_file
            _address[task] = []
            _result[task] = {}
            self.request.send('well: task init success')
            return

        # receive client exec task request
        if task in _task and size == 1:
            _address[task].append(address)
            # HOOD send matrix to client
            pass
            return

        # receive result of client, maybe have some data is not finish, we'll need send those data to other client.
        if task in _task and size > 1:
            pass


def run():
    total_server = socketserver.TCPServer(('0.0.0.0', 17788), TotalSocketServer)
    total_server.serve_forever()
