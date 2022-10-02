import play_rec_audio
import pyttsx3
from time import sleep
from threading import Thread
from queue import SimpleQueue
import keyboard
import os

#--------------------#
#--------Input-------#

input_q = SimpleQueue()         # stores input events


# Button Input - can detect multi-presses from buttons
class PressCounter:
    def __init__(self):
        self.timer = 0
        self.timer_standard = 5     # this number * 0.05 second intervals - essentially the multi-click timeout
        self.press_count = 0

        keyboard.add_hotkey('space', self.add_press) # ctrl+up+

        count_down_thread = Thread(target=self.countdown)
        count_down_thread.daemon = True
        count_down_thread.start()

    def countdown(self):
        while True:
            while self.timer > 0:
                sleep(0.05)
                self.timer -= 1
            if self.press_count > 0 and self.timer == 0:
                button_action(self.press_count) # send the number of presses to the button_action function
                self.press_count = 0            # reset press count
            sleep(0.01)

    def add_press(self):
        self.press_count += 1
        self.timer = self.timer_standard

# Text Input
"""
keyboard.add_hotkey('ctrl+space', text_input)

def text_input():
    i = input('type here: ')
    input_event_q.put(i)             # put press_num in the processor queue
"""

# send button input
def button_action(press_num):
    assert isinstance(press_num, int)
    map = {
        1:'btnA*1',
        2:'btnA*2',
        3:'btnA*3',
        4:'btnA*4',
        10:'btnA*10'
    }
    action = map.get(press_num)
    if action:
        input_q.put(action)     # put action in the action queue
    else:
        pass
        # put an error in the error log/panel??

#--------------------#

# the object to record audio
rec = play_rec_audio.RecAudio()         # other processes can call function of this object


#--------------------#
#-------Output-------#

# NOTE: TEMP NOTES!!

# OUTPUT - handles rich for display and audio for output

    # queue to handle all output requests
        # audio
            # >>> audio must be managed to automatically stop audio when new requests are entered
            # tts audio
            # play custom audio / play pre-defined chimes
            # specific thing for alarm - pauses current audio, and then loops an audio recording until alarm is stoped
        # visual
            # print to rich panel
            # print to terminal

# what needs to be passed to queue
    # a tuple or ditionary with:
        # function name
        # function arguments
        # (maybe other stuff for tracking?)

#--------------------#

# NOTE: THIS NEEDS TO BE HANDLED
visual_mode = False


# class for any audio output - has functions for tts and playing recordings
class AudioOutput:
    def __init__(self):
        # instantiate class for playing audio from the play_rec_audio module
        self.program_sounds = play_rec_audio.PlayAudio()    # one instance for playing tts and program notifcation sounds
        self.general_sounds = play_rec_audio.PlayAudio()    # one instance for playing general audio

        self.tts_current_message = ''
        self.tts_audio_path = './program_files/current_tts.wav'
        self.tts = pyttsx3.init()                       # initialize the tts engine from the pyttsx3 module

        self.tones_path = './program_files'


    # all program_sounds functions:

    def play_tone(self, tone_type):
        # check if general_sounds is playing
        if self.general_sounds.state == "playing":
            self.pause_soundfile()
        # map of tone_type's file name
        map = {
            1:'tone_1_5.wav',
            2:'tone_5_1.wav'
        }
        path = os.path.join(self.tones_path, map.get(tone_type))
        try:
            self.program_sounds.play(path)
        except:
            # ERROR
            pass 

    def set_tts_speed(self, rate):
        self.tts.setProperty('rate', rate)          # defualt speaking rate is 200

    def tts_speak(self, message):
        # check if general_sounds is playing
        if self.general_sounds.state == "playing":
            self.pause_soundfile()
        path = self.tts_audio_path
        if message != self.tts_current_message:     # if the message is the same, skip this step
            self.tts.save_to_file(message, path)
            self.tts.runAndWait()
        self.tts_current_message = message
        self.program_sounds.play(path)
    
    def pause_program_sounds(self):
        self.program_sounds.pause_toggle()

    def stop_program_sounds(self):
        self.program_sounds.stop()


    # all general_sounds functions:

    def play_soundfile(self, filepath):
        self.stop_soundfile()               # first stops audio if it's playing
        self.general_sounds.play(filepath)

    def pause_soundfile(self):
        self.general_sounds.pause_toggle()

    def stop_soundfile(self):
        self.general_sounds.stop()


#--------------------#
#-----MAIN_SCRIPT----#

# this script should only be executed as a module
if __name__ == "__main__":
    pass
else:
    pc = PressCounter()         # detects button presses
    audio = AudioOutput()       # instatiate the AudioOutput class 
