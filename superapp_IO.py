from turtle import color
import play_rec_audio
import pyttsx3
from time import sleep
from threading import Thread
from queue import SimpleQueue
import keyboard
import os

from rich.console import Console
from rich.table import Table

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

        # start the thread that will 
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


# class for visual output
class VisualOutput:
    def __init__(self):
        self.visual_output_q = SimpleQueue()     # the queue for accepting output requests

        self.rich_console = Console()

        do_requests_thread = Thread(target=self.do_visual_output_requests)
        do_requests_thread.daemon = True
        do_requests_thread.start()

    def do_visual_output_requests(self):
        func_map = {
            'print_notes_table':self.print_notes_table,
            'print_user_message':self.print_user_message,
            'print_program_message':self.print_program_message
        }
        while True:
            request = self.visual_output_q.get()
            try:
                function_name = request[0]
                function = func_map.get(function_name)
                try:
                    argument = request[1]
                    function(argument)
                except:
                    function()
            except:
                print("output error")
    
    #---

    # for printing messages to the user
    def print_user_message(self, message):
        self.rich_console.print(message, style='dark_slate_gray1')

    def print_program_message(self, message):
        self.rich_console.print(message, style='green4')

    # for print
    def print_notes_table(self, table_data_list):
        table = Table(title="a table", show_lines=True)
        # add a column to number the rows
        table.add_column('#', justify="center", no_wrap=True)
        # take the first item of the list and use it to create columns
        for column_name in table_data_list[0]:
            if column_name == "Time":
                table.add_column(column_name, justify="left", style="dark_orange3", overflow='fold', min_width=20)
            elif column_name == "Title":
                table.add_column(column_name, justify="left", style="cyan", overflow='fold', min_width=30)
            elif column_name == "Descriptor":
                table.add_column(column_name, justify="left", style="cyan", overflow='fold', min_width=30)
            elif column_name == "File Path":
                table.add_column(column_name, justify="left", style="wheat4", overflow='ellipsis', max_width=20)
            else:
                table.add_column(column_name, justify="left", style="purple4", overflow='ellipsis')
        # then remove the first item (the one for the columns) and add the other elements as rows
        table_data_list.pop(0)
        row_number = 1
        for row in table_data_list:
            table.add_row(str(row_number), *row)         # the `*` works like it would passing arguments to a function - it unpacks the tuple (https://www.w3schools.com/python/python_tuples_unpack.asp)
            row_number += 1
        # finally, print the table
        self.rich_console.print(table)
        


#--------------------#
#-----MAIN_SCRIPT----#

# NOTE: THIS NEEDS TO BE HANDLED
visual_mode = False

# this script should only be executed as a module
if __name__ == "__main__":
    pass
else:
    input_q = SimpleQueue()             # stores input events
    binput = ButtonInput()              # detects button presses
    rec = play_rec_audio.RecAudio()     # other processes can call function of this object
    audio_out = AudioOutput()           # instatiate the AudioOutput class 
    visual_out = VisualOutput()         # instatiate the VisualOutput class 
