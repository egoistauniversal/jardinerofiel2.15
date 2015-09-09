import serial


class SerialUSB(object):
    def __init__(self):
        self._port = '/dev/ttyACM0'
        self._bauds = '57600'
        self._timeout = 0
        self._mySerial = None
        self._temporary_data = ''
        self.error = False
        self.message = ''
        self._detect_serial_connection()

    def _detect_serial_connection(self):
        try:
            self._mySerial = serial.Serial(self._port, self._bauds, timeout=self._timeout)
            self.message = 'Connexion correcta con el arduino en ' + self._port
        except Exception, e:
            self.error = True
            self.message = str(e) + ' - Error al conectar con el arduino'

    def send_data(self, data):
        self._mySerial.write(data)

    def read_data(self):
        _data = []
        # Read serial data from Arduino
        while len(_data) == 0:
            _data = self._mySerial.readlines()
        _value = _data[0].strip()
        # print _data
        return _value

    def close(self):
        if not self.error:
            self._mySerial.close()

