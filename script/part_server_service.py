# coding: utf-8

import socketserver
import struct
import json
import hashlib

# global variable, list is task name, to avoid multi tasks
_task = []


# generate md5 of specify message
def md5(message):
    sha = hashlib.sha256()
    sha.update(message)
    return sha.hexdigest()


# Deal with task with subprocess
def deal_with_task(task):
    print(task)
    pass


class TotalSocketServer(socketserver.BaseRequestHandler):

    def handle(self):
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
        if task not in _task and size == 1:
            _task.append(task)
            deal_with_task(task)

        self.request.send('fail: the task is exists')


def run():
    total_server = socketserver.TCPServer(('0.0.0.0', 17778), TotalSocketServer)
    total_server.serve_forever()
