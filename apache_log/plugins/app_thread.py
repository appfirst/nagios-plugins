
import logging
import socket
import select
from threading import Thread


LOGGER = logging.getLogger(__name__)



class ProcessThread(Thread):


    def __init__(self, host = '127.0.0.1', port = 30310):
        super(ProcessThread, self).__init__()
        self.running = True
        self._socket = None
        self._data = None
        self.host = host
        self.port = port


    def setData(self, data):
        LOGGER.debug(' set data {i}'.format(i=data))
        self._data = data

    def stop(self):
        LOGGER.debug ('ProcessThread stop')
        self.running = False
        self._socket.shutdown(socket.SHUT_WR)
        self._socket.close()

    def checkData(self):

        try:
            LOGGER.debug ('socket accept')
            client, addr = self._socket.accept()
            ready = select.select([client,],[], [],2)
            if ready[0]:
                LOGGER.debug ('client.recv...')
                data = client.recv(512)
                LOGGER.debug ('client.send...')
                if self._data is not None:
                    client.send(str(self._data))
                else:
                    client.send(str(-1))
                LOGGER.debug ('data was received:' + data)
                self._data = None;
                return True
        except KeyboardInterrupt:
            self._socket.close()
            LOGGER.debug('stop.')
        except socket.error, msg:
            self._socket.close()
            LOGGER.debug ('socket error: %s' % msg)

        return False

    def run(self):

        if self._socket is None:
            self._socket = socket.socket()

            self._socket.bind((self.host, self.port))
            LOGGER.debug('Listening on {h} {p}...'.format(p = self.port, h = self.host))
            self._socket.listen(10)

        while self.running:
            try:
                LOGGER.debug('server running ...')
                self.checkData()
                # time.sleep(1)
            except KeyboardInterrupt:
                self.stop()




