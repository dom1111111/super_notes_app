import pyttsx3
from time import sleep
from threading import Thread
from queue import SimpleQueue
import keyboard
import os
from rich.console import Console

import play_rec_audio

#--------------------#
#--------Input-------#

# Button Input - can detect multi-presses from buttons
class ButtonInput:
    def __init__(self):
        self.timer = 0
        self.timer_standard = 5     # this number * 0.05 second intervals - essentially the multi-click timeout
        self.press_count = 0

        # start the thread that will detect button input
        self.continually_detect_button_presses()

        # start the thread that will determine how many button presses happen at a time
        count_down_thread = Thread(target=self.countdown)
        count_down_thread.daemon = True
        count_down_thread.start()

    # detect button presses and call the `add_press` function
    def continually_detect_button_presses(self):
        keyboard.add_hotkey('space', self.add_press) # ctrl+up+

    # if this function is called (meaning a button was pressed function), increase the press count and reset the timer
    def add_press(self):
        self.press_count += 1
        self.timer = self.timer_standard

    # if the countdown reaches 0 (meaning no button presses happened in the timeout period), send the number of presses to `button_action`
    def countdown(self):
        while True:
            while self.timer > 0:
                sleep(0.05)
                self.timer -= 1
            if self.press_count > 0 and self.timer == 0:
                self.button_action(self.press_count) # send the number of presses to the button_action function
                self.press_count = 0            # reset press count
            sleep(0.01)

    # send button input - actions depends on number of presses within the timeout period
    def button_action(self, press_num):
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

# Text Input
"""
keyboard.add_hotkey('ctrl+space', text_input)

def text_input():
    i = input('type here: ')
    input_event_q.put(i)             # put press_num in the processor queue
"""


#--------------------#
#-------Output-------#

# class for audio output
class AudioOutput:
    def __init__(self):
        # instantiate class for playing audio from the play_rec_audio module
        self.program_sounds = play_rec_audio.PlayAudio()    # one instance for playing tts and program notifcation sounds
        self.general_sounds = play_rec_audio.PlayAudio()    # one instance for playing general audio
        # text to speech - robot voice output
        self.tts_current_message = ''
        self.tts_audio_path = './program_files/current_tts.wav'
        self.tts = pyttsx3.init()                       # initialize the tts engine from the pyttsx3 module
        # program tones file path
        self.tones_path = './program_files'

    def get_program_sounds_state(self):
        return self.program_sounds.get_audio_state()

    def get_general_sounds_state(self):
        return self.general_sounds.get_audio_state()

    #---
    # all program_sounds functions:

    def play_program_tone(self, tone_type):
        # first stops audio (and closes stream) if it's playing
        self.stop_program_sounds()
        # check if general_sounds is playing
        if self.general_sounds.get_audio_state() == "active":
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
        # if general_sounds is paused, then resume playback
        if self.general_sounds.get_audio_state() == "stopped":
            self.pause_soundfile()

    def set_tts_speed(self, rate):
        self.tts.setProperty('rate', rate)          # defualt speaking rate is 200

    def tts_speak(self, message):
        # first stops audio (and closes stream) if it's playing
        self.stop_program_sounds()
        # check if general_sounds is playing
        if self.general_sounds.get_audio_state() == "active":
            self.pause_soundfile()
        # create tts audio file from message and then play it
        if message != self.tts_current_message:     # if the message is the same, skip this step
            self.tts.save_to_file(message, self.tts_audio_path)
            self.tts.runAndWait()
        self.tts_current_message = message
        self.program_sounds.play(self.tts_audio_path)
        # if general_sounds is paused, then resume playback
        if self.general_sounds.get_audio_state() == "stopped":
            self.pause_soundfile()

    def tts_speak_and_wait(self, message):
        self.tts_speak(message)
        # this loop ensures that the tts audio output is completed before moving on
        while self.get_program_sounds_state() == "active":
            sleep(0.1)

    def pause_program_sounds(self):
        self.program_sounds.pause_toggle()

    def stop_program_sounds(self):
        self.program_sounds.stop()

    #---
    # all general_sounds functions:

    def play_soundfile(self, filepath):
        self.stop_soundfile()               # first stops audio if it's playing
        self.general_sounds.play(filepath)

    def pause_soundfile(self):
        self.general_sounds.pause_toggle()

    def stop_soundfile(self):
        self.general_sounds.stop()


# class for visual output
class VisualOutput:
    def __init__(self):
        # for rich visual output
        self.rich_console = Console()

    # for printing messages to the user
    def print_user_message(self, message):
        self.rich_console.print(message, style='dark_slate_gray1')

    def print_program_message(self, message):
        self.rich_console.print(message, style='green4')

    # for printing rich tables
    def print_rich_table(self, rich_table):
        # only print table if it is indeed a rich.table object
        if str(type(rich_table)) == "<class 'rich.table.Table'>":
            self.rich_console.print(rich_table)
        else:
            self.print_program_message('ERROR - Incorrect object supplied for table making')


#--------------------#
#-----MAIN_SCRIPT----#

# if set to false, then don't do visual output
visual_mode = True
## this curently does nothing

# this script should only be executed as a module
if __name__ == "__main__":
    pass
else:
    input_q = SimpleQueue()             # stores input events
    binput = ButtonInput()              # detects button presses
    rec = play_rec_audio.RecAudio()     # other processes can call function of this object
    audio_out = AudioOutput()           # instatiate the AudioOutput class 
    visual_out = VisualOutput()         # instatiate the VisualOutput class 
