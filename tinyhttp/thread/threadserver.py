from threading import Thread, current_thread

from ..http.server import HttpServer
from ..helper import Signal, argv


class ThreadHttpServer(HttpServer):
    def _run(self):
        self.sock.listen(self.backlog)
        while True:
            sock, addr = self.sock.accept()
            # debug
            if Signal.debug:
                print('Connect by {} Port {}'.format(*addr))
            Thread(target=self._echo, args=(sock,)).start()


def main():
    port = 6789
    if len(argv) > 1:
        port = int(argv[1])
    serv = ThreadHttpServer(port=port)
    try:
        serv()
    except KeyboardInterrupt:
        Signal.go = False
        print('\x08\x08Good bye', flush=True)
