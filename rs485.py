import serial
import RPi.GPIO as GPIO

BAUD = 115200
RS485_REDE_PIN = 23

class RS485:
    def __init__(self, baudrate):
        self.port = serial.Serial(baudrate=baudrate, bytesize=8, parity=serial.PARITY_NONE, port="/dev/serial0", rtscts=0,
                             xonxoff=0, stopbits=1, timeout=None)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RS485_REDE_PIN, GPIO.OUT)
        GPIO.output(RS485_REDE_PIN, GPIO.LOW)
        self.locked = False

    """
    :param: msg: bytearray, message to send
    """
    def sendRS485(self, msg, answerWanted):
        if self.locked == False:
            self.locked = True
            GPIO.output(RS485_REDE_PIN, GPIO.HIGH)
            self.port.write(msg)
            GPIO.output(RS485_REDE_PIN, GPIO.LOW)
        else:
            return False

        if answerWanted == False:
            self.locked = False

    def receiveRS485(self, length):
        self.port.read(length)
        self.locked = False