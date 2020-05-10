#!/bin/python3

import os, subprocess, time, threading
import mlcomm

background_music = "/home/pi/modulocks_center/sounds/background_music.mp3"
main_sound_dir = "/home/pi/modulocks_center/sounds/"

fade_out_time = 0.01  # not exact timing
low_background_volume = 50  # background music volume when playing an effect
current_vol = 100

executer_max_timeout = 60

background = subprocess.Popen(
    ['mplayer', '-slave', '-channels', '6', '-ao', 'pulse', '-quiet', '-loop', '0', background_music],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.PIPE)


def background_fade_out():
    global current_vol

    while current_vol > low_background_volume:
        current_vol -= 5
        if current_vol < low_background_volume:
            current_vol = low_background_volume

        command = "volume " + str(current_vol) + " 100\r\n"
        background.stdin.write(command.encode("UTF-8"))
        background.stdin.flush()


def background_fade_in():
    global current_vol

    while current_vol < 100:
        current_vol += 5
        if current_vol > 100:
            current_vol = 100

        command = "volume " + str(current_vol) + " 100\r\n"
        background.stdin.write(command.encode("UTF-8"))
        background.stdin.flush()
        # time.sleep(fade_out_time/(100-low_background_volume))


def play(item):
    background_fade_out()
    os.system("mplayer -ao pulse -volume 100 -channels 6 " + main_sound_dir + item + " -quiet -slave 2> /dev/null")
    background_fade_in()
    print('--> done')

def main_center_thread():
    nodeList = mlcomm.nodeMapping()

    while True:
        for node in nodeList:
            resp_cmd, resp_data = mlcomm.whatsup(node)
            if resp_cmd == mlcomm.commands['DOIT']:
                if resp_data[0] == b'\x01':
                    print("Node ", str(node), " solved.")
                    music = resp_data[12:].decode()
                    play(music)
                    if mlcomm.executer_present:
                        mlcomm.execute(resp_data[1:12])
                        mlcomm.receiveAnswer('ACK', executer_max_timeout)     # waiting for the executer to finish

            if resp_cmd == mlcomm.commands['SOLVE_BUTTON']:
                if resp_data[0] != b'\x00':
                    to_solve = int.from_bytes(resp_data, byteorder='little')
                    print("Solve button pressed: ", str(to_solve))
                    # TODO if node does not answer
                    mlcomm.solveGame(to_solve)

            if resp_cmd == mlcomm.commands['LANG_SEL']:
                if resp_data[0] != b'\x00':
                    new_lang = int.from_bytes(resp_data, byteorder='little')
                    print("Language changed to: ", new_lang)
                    # TODO language selection
                    pass

print("Started")
t = threading.Thread(target=main_center_thread)
t.start()