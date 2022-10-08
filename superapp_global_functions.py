from queue import SimpleQueue, Queue
import speech_recognition as sr
from datetime import datetime
from time import sleep
import os

import superapp_IO as io

#--------------------#

def get_input():
    return io.input_q.get()

def command_input():
    while True:
        b_input = get_input()
        if b_input == 'btnA*1':
            return 'A1'
        elif b_input == 'btnA*2':
            return 'A2'
        elif b_input == 'btnA*3':
            output_play_tone(2)
            print('command cancelled')
            return 'reset'
        """
        elif b_input == 'btnA*4':
            # help
            return
        """

#--------------------#

def get_current_datetime_string():
    now = datetime.now()
    datetime_string = now.strftime('%Y-%m-%d_%H%M%S%f')[:-3]
    return datetime_string

def generate_file_path(filename:str, folder:str=''):
    script_path = os.path.relpath(__file__)        # gets the full file path of this script, including file name
    script_dir = os.path.dirname(script_path)       # gets the file path of this script, NOT including file name
    if folder:
        folder_path = os.path.join(script_dir, folder)    # join the script file path with folder name
    else:
        folder_path = script_dir
    new_path = os.path.join(folder_path, filename)        # join the script file path with file name
    return new_path

#--------------------#

def output_do_visual_function(function, argument):
    request = (function, argument)
    io.visual_out.visual_output_q.put(request)

def output_play_tone(tone_type):
    io.audio_out.play_tone(tone_type)

def output_tts(message):
    io.audio_out.tts_speak(message)

def stop_program_sounds():
    io.audio_out.stop_program_sounds()


def input_record_start():
    io.rec.record()

def input_record_stop():
    io.rec.stop_and_return()

def input_record_stop_and_write(path):
    sleep(0.1)
    audio = io.rec.stop_and_return()
    io.rec.write_to_file(audio, path)


def transcribe_audio_file(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)
    try:
        recognized_audio = r.recognize_google(audio)
        return recognized_audio
    except sr.WaitTimeoutError:
        pass
        # return ("ERROR", "the program assumed you were done speaking")
    except sr.UnknownValueError:
        pass
        # return ("ERROR", "Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        pass
        # return ("ERROR", f"Could not request results from Google Speech Recognition service; {e}")
    except:
        pass
        # return ("ERROR", "something went wrong")
