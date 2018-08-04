import asyncio

from ..http.server import HttpServer
from ..helper import Signal, argv, logging, to_bytes


class AsyncHttpServer(HttpServer):
    def __init__(self, port=8888, addr='0.0.0.0'):
        self.port = port
        self.addr = addr

    async def _send_body(self, conn):
        result = self._get_body(conn)
        conn = next(result)
        try:
            for fp in result:
                conn.write(fp)
                await conn.drain()
        except BrokenPipeError as e:
            print(e)
        except ConnectionResetError as e:
            print(e)

    async def _echo(self, reader, writer):
        try:
            req_head = await reader.read(1024)
        except BrokenPipeError as e:
            print(e)
        else:
            if not req_head:
                return
            head = self._get_head(req_head)
            head = head.replace('STATUS_CODE', str(self.status))
            writer.write(to_bytes(head))
            # writer.write(head.encode('ascii'))
            await self._send_body(writer)
            logging.info('HTTP/1.1 %s GET %s' % (self.status, Signal.path))
            if Signal.debug:
                print('\nReceived: %s' % req_head)
                print('\nSend headers: %s' % head)
                print('-'*36)
        writer.close()

    def _run(self):
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(
            self._echo, self.addr, self.port, loop=loop)
        server = loop.run_until_complete(coro)
        loop.run_forever()
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

    def __call__(self):
        print('Listening in http://localhost:%s port.' % self.port)
        self._run()


def main():
    port = 6789
    if len(argv) > 1:
        port = int(argv[1])
    serv = AsyncHttpServer(port=port)
    try:
        Signal.mode = 'Async'
        serv()
    except KeyboardInterrupt:
        Signal.go = False
        print('\x08\x08Good bye', flush=True)
