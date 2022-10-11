import speech_recognition as sr
from datetime import datetime
from time import sleep
import os

import superapp_IO as io
import app_notes_tasks as app_nota

#--------------------#
# misc utility functions

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

#--------------------#
# io input functions

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
            Output.play_tone(2)
            print('command cancelled')
            return 'reset'
        """
        elif b_input == 'btnA*4':
            # help
            return
        """

#--------------------#
# io audio record functions

class AudioRec:
    def start():
        io.rec.record()

    def stop():
        io.rec.stop_and_return()

    def stop_and_write(path):
        sleep(0.1)
        audio = io.rec.stop_and_return()
        io.rec.write_to_file(audio, path)

#--------------------#
# io output functions

class Output:
    def play_tone(tone_type):
        io.audio_out.play_program_tone(tone_type)

    def user_message(message):
        io.visual_out.print_user_message(message)
        io.audio_out.tts_speak(message)

    def program_message(message):
        io.visual_out.print_program_message(message)

    def stop_program_sounds():
        io.audio_out.stop_program_sounds()

#--------------------#
# notes_tasks_app functions

class AppNotesTasks:

    def quick_memo():
        Output.user_message("this command is currently unavailable")
    #### - stuff for quick voice memo - each note to be reviewed and added to notes app later
        time = get_current_datetime_string()
        folder_path = generate_file_path('files', 'storage')
        note_id = time + '_note.wav'
        audio_file_path = generate_file_path(note_id, folder_path)
    ####

    def create_full_note(audio_text:str):
        time = get_current_datetime_string()
        # 1) split the audio text into title and descriptor according to the split word
        try: # only do this if audio text is properly returned
            audio_text_words = audio_text.split()
        except:
            return
        split_word = ("descriptor")
        ## only do this if the split word is present
        if split_word in audio_text_words:
            split_index = audio_text_words.index(split_word)
            ## seperate text into command and content
            title_words = audio_text_words[0:split_index]
            descriptor_words = audio_text_words[split_index+1:]
            title = ' '.join(title_words)
            descriptor = ' '.join(descriptor_words)
        else:
            Output.program_message('ERROR - cancelled create_full_note')
            Output.user_message('Error; unable to complete command')
       
        # confirm with the user that the input is correct
        confirmation_message = f"""creating note with title: "{title}", and descriptor: "{descriptor}". Press once to confirm, and twice or more to cancel"""
        Output.user_message(confirmation_message)
        u_input = command_input()               # blocks, waiting for button input
        Output.stop_program_sounds()            # stop tts audio if still playing
        if u_input == 'A1': 
            pass                                # go on to the next step
        elif u_input == 'A2' or u_input == 'reset':
            return                              # cancel function 
        # finally, execute the query
        try:
            app_nota.create_note(time, title, descriptor)
        except:
            Output.program_message('ERROR - cancelled create_full_note')
            Output.user_message('Error; something went wrong, note not created')

    # function to be used by notes output functions for creating tables
    ## must ensure that queries to the db use this order or columns
    def display_result_table(result):
        table_data = list(result)
        column_names = ('Time', 'Title', 'Descriptor', 'File Path')
        table_data.insert(0, column_names)
        io.visual_out.print_notes_table(table_data)

    def get_recent_notes():
        result = app_nota.get_last_50_notes()
        AppNotesTasks.display_result_table(result)

    def full_search(value:str):
        try:
            Output.program_message(f'(full_search) searching for "{value}"')
            matches = app_nota.get_sorted_notes_with_value(value)
            AppNotesTasks.display_result_table(matches)
        except:
            Output.program_message('ERROR - full search cancelled')
            Output.user_message('Error; something went wrong')
