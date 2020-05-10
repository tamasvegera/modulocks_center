#!/bin/python3
import rs485

BROADCAST_ADDRESS           = 0x00
CENTER_ADDRESS              = 0x01
CENTER_EXECUTER_ADDRESS     = 0x02
LANGUAGE_SELECTOR_ADDRESS   = 0x03
GAME_SOLVE_TABLE_ADDRESS    = 0x04

NODE_START_ADDRESS          = 0x10

executer_present = False

packet_overhead_length = 7      # packet length - data length
commands = {
    'PING':         0x01,
    'ACK':          0x02,
    'NACK':         0x03,
    'SOLVE_GAME':   0x04,
    'WHATSUP':      0x05,
    'DOIT':         0x06,
    'SOLVE_BUTTON': 0x07,
    'LANG_SEL':     0x08,
    'EXECUTE':      0x09
}

answerWantedLUT = {
    'PING':         True,
    'ACK':          False,
    'NACK':         False,
    'SOLVE_GAME':   True,
    'WHATSUP':      True,
    'DOIT':         False,
    'SOLVE_BUTTON': False,
    'LANG_SEL':     False,
    'EXECUTE':      True
}

commandDataLengths = {
    'PING':         0,
    'ACK':          0,
    'NACK':         0,
    'SOLVE_GAME':   0,
    'WHATSUP':      0,
    'DOIT':         32,
    'SOLVE_BUTTON': 1,
    'LANG_SEL':     1,
    'EXECUTE':      11
}

bus = rs485.RS485()

def sendCommand(command, data, destination):
    """
    :param command:     string, element of commands{}
    :param data:        bytearray, data to send
    :param destination: 1 byte int, destination node address
    :return: -
    """
    packet = b'\x02'     # start byte

    packet += destination.to_bytes(1, byteorder='big')
    packet += commands[command].to_bytes(1, byteorder='big')
    packet += len(data).to_bytes(1, byteorder='big')
    packet += data
    checksum = 0

    for i in range(len(data)):
        checksum += data

    packet += checksum.to_bytes(2, byteorder='little')
    packet += b'\x03'

    bus.sendRS485(packet, answerWantedLUT[command])

def receiveAnswer(command, timeout = 1):
    """
    :param command: command to wait for
    :return: if answer contains command: data; else: False
    """
    packet = bus.receiveRS485(commandDataLengths[command] + packet_overhead_length, timeout)

    if packet:
        if packet[2] == commands[command]:
            data_length = packet[3]
            data_end = data_length + 4
            data = bytearray(packet[4: data_end])

            # TODO check checksum
            return data

        else:
            return False
    return False

def pingNode(address):
    """
    :param address:     node address to ping
    :return: True or False
    """
    sendCommand('PING', b'', address)
    result = receiveAnswer('ACK')

    if result == False:        # ACK has no data
        return False
    else:
        return True

def solveGame(address):
    """
    :param address: game node address to solve
    :return: if node acking: DOIT data, else False
    """

    sendCommand('SOLVE_GAME', b'', address)
    return receiveAnswer('DOIT')

def whatsup(address):
    """
    :param address: node address to ask
    :return: answer command, data
    """

    global GAME_SOLVE_TABLE_ADDRESS, LANGUAGE_SELECTOR_ADDRESS, NODE_START_ADDRESS

    sendCommand('WHATSUP', b'', address)

    if address == LANGUAGE_SELECTOR_ADDRESS:
        command = 'LANG_SEL'
        result = receiveAnswer(command)

    elif address == GAME_SOLVE_TABLE_ADDRESS:
        command = 'SOLVE_BUTTON'
        result = receiveAnswer(command)

    elif address >= NODE_START_ADDRESS:
        command = 'DOIT'
        result = receiveAnswer(command)

    if result != False:
        return command, result
    else:
        return False, False

def execute(data):
    """
    :param data: data to send to executer
    :return: True or False
    """
    global CENTER_EXECUTER_ADDRESS

    sendCommand('EXECUTE', data, CENTER_EXECUTER_ADDRESS)
    result = receiveAnswer('ACK')

    if result == b'':
        return True
    else:
        return False

def nodeMapping():
    """
    :return: array of active node addresses including fixed node addresses
    """
    global CENTER_ADDRESS, BROADCAST_ADDRESS, executer_present
    nodeList = []

    for addr in range(20):      # TODO set range to 256!!!!!
        if addr != CENTER_ADDRESS and addr != BROADCAST_ADDRESS:
            if(pingNode(addr)):
                if addr == CENTER_EXECUTER_ADDRESS:
                    executer_present = True
                else:
                    nodeList.append(addr)

    print("Nodes mapped:")
    print(nodeList)
    return nodeList