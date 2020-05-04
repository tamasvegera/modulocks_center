import rs485

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

def sendCommand(command, data):
    