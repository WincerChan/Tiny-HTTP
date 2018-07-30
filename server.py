from socket import AF_INET, SOCK_STREAM, socket
from sys import argv
import logging
from threading import Thread, current_thread
from os import listdir, path as p

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s [%(threadName)s] %(message)s')


class Signal:
    go = True
    isdir = False
    path = ''


TYPE = {
    'txt': 'text/plain;',
    'png': 'image/png;',
    'jpg': 'image/jpg;',
    'html': 'text/html;',
    'js': 'application/javascript;',
    'css': 'text/css;',
    'pdf': 'application/pdf;',
    'gif': 'image/gif;',
}


def list_files():
    html = '<h1>%s dictory.</h1><hr/><ul>' % Signal.path

    for file in listdir('.' + Signal.path):
        if p.isdir('.'+Signal.path + file):
            file += '/'
        html += '<li style="font-size: 1.2em"><a href=%s>%s</a></li>' % (
            Signal.path + file, file)
    return html + '</ul>'


def parse_url(url, file_lengths)->str:
    params = {}
    if Signal.isdir:
        content_type = 'text/html'
    else:
        path = url.decode('utf-8').split(' ')[1]
        suffix = path.split('.')[-1]
        content_type = TYPE.get(suffix, 'application/octet-stream')
    # 目录名
    if p.isdir('.'+Signal.path) and not Signal.path.endswith('/'):
        Signal.path += '/'
        params['Location'] = Signal.path
    params['Content-Length'] = file_lengths
    params['Content-Type'] = content_type
    params['Date'] = 'Sun, 29 Jul 2018 00:30:00 GMT'
    params['Server'] = 'Python'
    return params


def transfer_encoding(func):
    def chunked(*args):
        result = func(*args)
        conn = next(result)
        try:
            for fp in result:
                conn.send(fp)
        except BrokenPipeError:
            pass
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
    def _open_file(self, req_head):
        req = req_head.decode('utf-8')
        Signal.path = req.split(' ')[1]
        try:
            open('.%s' % Signal.path, 'rb')
            Signal.isdir = False
        except FileNotFoundError:
            self.status = 404
        except IsADirectoryError:
            Signal.isdir = True
            self.status = 200
        else:
            self.status = 200
            from os.path import getsize
            return getsize('.%s' % Signal.path)

    @transfer_encoding
    def _get_body(self, conn) -> str:
        yield conn
        if self.status == 200:
            try:
                fp = open('.%s' % Signal.path, 'rb')
                Signal.isdir = False
            except IsADirectoryError:
                Signal.isdir = True
                html = list_files()
                yield html.encode('ascii')
            else:
                for x in fp:
                    yield x
        elif self.status == 404:
            yield b'404 File Not Found.'
        elif self.status == 405:
            yield b'405 Not Allowed Method.'
        elif self.status == 301:
            yield ('301 to %s' % Signal.path).encode('ascii')

    def _get_head(self, head):
        file_length = self._open_file(head)
        params = parse_url(head, file_length)
        headers = 'HTTP/1.1 STATUS_CODE\r\n'
        if not head.startswith(b'GET'):
            self.status = 405
        for key, value in params.items():
            if key == 'Location':
                self.status = 301
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
            head = self._get_head(req_head)
            head = head.replace('STATUS_CODE', str(self.status))
            sock.send(head.encode('ascii'))
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
