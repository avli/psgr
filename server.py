import argparse
import os
import socket
import sys


_200 = 'HTTP/1.0 200 OK\r\n'.encode('utf-8')
_400 = 'HTTP/1.0 400 Bad Request'.encode('utf-8')
_404 = 'HTTP/1.0 404 Not Found\r\n\r\nnot found\n'.encode('utf-8')
_405 = 'HTTP/1.0 405 Method Not Allowed\r\n\r\nnot allowed\n'.encode('utf-8')


def respond(req, fd):
    req = req.decode('utf-8')
    if not req.startswith('GET'):
        fd.sendall(_405)
        return
    try:
        path = req.split(' ')[1].lstrip('/') or 'index.html'
    except IndexError:
        fd.sendall(_400)
        return
    try:
        with open(path, 'rb') as f:
            content = f.read()
        res = _200
        if os.path.splitext(path)[1].lower() == '.html':
            res += 'Content-type: text/html\r\n\r\n'.encode('utf-8')
        else:
            res += 'Content-type: text/plain\r\n\r\n'.encode('utf-8')
        res += content
        fd.sendall(res)
    except IOError:
        fd.sendall(_404)


def serve(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        while True:
            conn, addr = s.accept()
            with conn:
                if os.fork() == 0:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        respond(data, conn)


def main():
    parser = argparse.ArgumentParser(description="A simple HTTP GET requests servers")
    parser.add_argument('host', type=str)
    parser.add_argument('port', type=int)
    args = parser.parse_args(sys.argv[1:])
    serve(args.host, args.port)


if __name__ == '__main__':
    main()
