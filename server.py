from socket import AF_INET, SOCK_STREAM, socket
from sys import argv
import logging
from threading import Thread, current_thread

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s [%(threadName)s] %(message)s')


class Signal:
    go = True


def parse_url(url)->str:
    params = {}
    params['Transfer-Encoding'] = 'chunked'
    params['Content-Type'] = 'text/plain;'
    params['Date'] = 'Sun, 29 Jul 2018 00:30:00 GMT'
    params['Server'] = 'Python'
    return params


def transfer_encoding(func):
    def chunked(*args):
        result, conn = func(*args)
        lens = hex(len(result))[2:]
        first = lens.encode('ascii') + b'\r\n'
        last = b'\r\n0\r\n\r\n'
        conn.send(first + result + last)
    return chunked


class EchoServer:
    def __init__(self, port=8888, addr='0.0.0.0', family=AF_INET,
                 type_=SOCK_STREAM, backlog=0, init=True):
        self.addr = addr
        self.port = port
        self.family = family
        self.type_ = type_
        self.backlog = backlog

    def _echo(self, sock: socket):
        while True:
            try:
                req_head = sock.recv(1)
                # print('Received: ', req_head)
            except BrokenPipeError:
                break
            else:
                if not req_head:
                    break
                sock.send(req_head)
            print('Send: ', req_head)

    def _run(self):
        self.sock.listen(self.backlog)
        while True:
            sock, addr = self.sock.accept()
            print('Connect by {} Port {}'.format(*addr))
            self._echo(sock)

    def __call__(self):
        self.sock = socket(self.family, self.type_)
        self.sock.bind((self.addr, self.port))
        print('Listen in %s porn.' % self.port)
        self._run()


class HttpServer(EchoServer):
    @transfer_encoding
    def _get_body(self, conn) -> str:
        body = 'Hello World'.encode('ascii')
        return body, conn

    def _get_head(self, head):
        params = parse_url(head)
        headers = 'HTTP/1.1 200\r\n'
        for key, value in params.items():
            if value:
                headers += '{}: {}\r\n'.format(key, value)

        return headers + '\r\n'

    def _echo(self, sock: socket):
        try:
            req_head = sock.recv(1024)
        except BrokenPipeError:
            return
        else:
            if not req_head:
                return
            if req_head.startswith(b'GET'):
                head = self._get_head(req_head)
                sock.send(head.encode('ascii'))
                print(head.encode('ascii'))
                self._get_body(sock)
        sock.close()

    def __call__(self):
        self.sock = socket(self.family, self.type_)
        self.sock.bind((self.addr, self.port))
        print('Listening in http://localhost:%s port.' % self.port)
        self._run()


class ThreadHttpServer(HttpServer):
    def _run(self):
        self.sock.listen(self.backlog)
        while True:
            sock, addr = self.sock.accept()
            print('Connect by {} Port {}'.format(*addr))
            Thread(target=self._echo, args=(sock,)).start()


if __name__ == '__main__':
    port = int(argv[1])
    serv = ThreadHttpServer(port=port)
    try:
        serv()
    except KeyboardInterrupt:
        Signal.go = False
        print('\x08\x08Good bye', flush=True)
        exit()
