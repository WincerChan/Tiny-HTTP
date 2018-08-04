from ..tcp import EchoServer
from ..helper import Signal, list_files, logging, parse_url, to_bytes, to_str
from socket import AF_INET, SOCK_STREAM, socket
try:
    from urllib.parse import unquote
except ImportError:
    print('Require Python3.5+')
    exit(1)


class HttpServer(EchoServer):
    def _open_file(self, req_head):
        req = to_str(req_head)
        encode_tmp = req.split(' ')[1]
        Signal.path = unquote(encode_tmp)
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

    def _get_body(self, conn) -> str:
        yield conn
        if self.status == 200:
            try:
                fp = open('.%s' % Signal.path, 'rb')
                Signal.isdir = False
            except IsADirectoryError:
                Signal.isdir = True
                html = list_files()
                yield to_bytes(html)
            else:
                for x in fp:
                    yield x
        elif self.status == 404:
            yield b'404 File Not Found.'
        elif self.status == 405:
            yield b'405 Not Allowed Method.'
        elif self.status == 301:
            yield to_bytes('301 to %s' % Signal.path)

    def _send_body(self, conn):
        result = self._get_body(conn)
        conn = next(result)
        try:
            for fp in result:
                conn.send(fp)
        except BrokenPipeError:
            pass

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
            sock.send(head.encode('utf-8'))
            self._send_body(sock)
            logging.info('HTTP/1.1 %s GET %s' % (self.status, Signal.path))
            if Signal.debug:
                print('\nReceived: %s' % req_head)
                print('\nSend headers: %s' % head)
                print('-'*36)
        sock.close()

    def __call__(self):
        self.sock = socket(self.family, self.type_)
        self.sock.bind((self.addr, self.port))
        print('Listening in http://localhost:%s port.' % self.port)
        self._run()
