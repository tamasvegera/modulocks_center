#!/bin/python3

import serial, time
import RPi.GPIO as GPIO

BAUD = 115200
RS485_REDE_PIN = 23

class RS485:
    def __init__(self, baudrate=BAUD):
        self.port = serial.Serial(baudrate=baudrate, bytesize=8, parity=serial.PARITY_NONE, port="/dev/ttyAMA0", rtscts=0,
                             xonxoff=0, stopbits=1, timeout=None)

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RS485_REDE_PIN, GPIO.OUT)
        GPIO.output(RS485_REDE_PIN, GPIO.LOW)
        self.locked = False

    def sendRS485(self, msg, answerWanted):
        """

        :param msg: bytearray, message to send
        :param answerWanted:    True or False
        :return: success, True or False
        """
        if self.locked == False:
            self.locked = True
            GPIO.output(RS485_REDE_PIN, GPIO.HIGH)
            self.port.write(msg)
            GPIO.output(RS485_REDE_PIN, GPIO.LOW)
        else:
            return False

        if answerWanted == False:
            self.locked = False

    def receiveRS485(self, length, timeout=5):
#        if self.port.timeout != timeout:
#            self.port.timeout = timeout

        start = time.time()

        while True:
            result = self.port.read(length)
            if result != b'' or time.time()-start >= timeout:
                break

        print(time.time()-start)
        self.locked = False
        return result