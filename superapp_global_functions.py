from queue import SimpleQueue, Queue
import speech_recognition as sr
from datetime import datetime
from time import sleep
import os

import superapp_IO as io

#--------------------#

def get_input():
    return io.input_q.get()

def check_input():
    input = get_input()
    if input == 'b1' or 'b2':
        return input
    elif input == 'reset':
        # call output to say "cancelled"
        return input
    elif input == 'help':
        pass

def tts(message):
    io.audio.tts_speak(message)

#--------------------#

def get_current_datetime_string():
    now = datetime.now()
    datetime_string = now.strftime('%Y-%m-%d_%H:%M:%S')
    return datetime_string

def get_current_datetime_string_filename_safe():
    now = datetime.now()
    datetime_string = now.strftime('%Y-%m-%d_%H-%M-%S')
    return datetime_string

def generate_file_path(filename:str, folder=''):
    script_path = os.path.realpath(__file__)        # gets the full file path of this script, including file name
    script_dir = os.path.dirname(script_path)       # gets the file path of this script, NOT including file name
    if folder:
        folder_path = os.path.join(script_dir, folder)    # join the script file path with folder name
    else:
        folder_path = script_dir
    new_path = os.path.join(folder_path, filename)        # join the script file path with file name
    return new_path

#--------------------#

def record_start():
    io.rec.record()

def record_stop_and_write(path):
    sleep(0.1)
    audio = io.rec.stop_and_return()
    io.rec.write_to_file(audio, path)

def full_record(path):
    io.rec.record()
    input = check_input()
    if input == 'bA_1' or input == 'bA_2':
        sleep(0.1)
        audio = io.rec.stop_and_return()
        io.rec.write_to_file(audio, path)
    elif input == 'reset':
        return

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

