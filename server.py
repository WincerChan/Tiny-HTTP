from socket import AF_INET, SOCK_STREAM, socket


class Signal:
    go = True


class EchoServer:
    def __init__(self, port=8888, addr='0.0.0.0', family=AF_INET,
                 type_=SOCK_STREAM, backlog=5, init=True):
        self.addr = addr
        self.port = port
        self.family = family
        self.type_ = type_
        self.backlog = backlog

    def _echo(self, sock: socket):
        while True:
            try:
                req_head = sock.recv(1)
                print('Received: ', req_head)
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


serv = EchoServer(port=5178)

try:
    serv()
except KeyboardInterrupt:
    Signal.go = False
    print('\x08\x08Good bye', flush=True)
    exit()
