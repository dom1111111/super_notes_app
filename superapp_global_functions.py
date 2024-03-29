import speech_recognition as sr
from datetime import datetime
from time import sleep
import os
from rich.table import Table

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
    Output.program_message("waiting for input")
    return io.input_q.get() # blocks, waiting for input to happen

def check_input():
    try:
        return io.input_q.get(block=False, timeout=0.01)
    except:
        return False

def command_input():
    while True:
        b_input = get_input()
        if b_input == 'btnA*1':
            return 'A1'
        elif b_input == 'btnA*2':
            return 'A2'
        elif b_input == 'btnA*3':
            Output.play_tone(2)
            Output.program_message('command cancelled')
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
        Output.wait_for_program_sounds()

    def user_message(message):
        io.visual_out.print_user_message(message)
        io.audio_out.tts_speak(message)
        Output.wait_for_program_sounds()

    def user_message_no_wait(message):
        io.visual_out.print_user_message(message)
        io.audio_out.tts_speak(message)

    def program_message(message):
        io.visual_out.print_program_message(message)

    def wait_for_program_sounds():
        # this loop ensures that any existing tts audio output is completed before moving on, but can be interupted by input
        while io.audio_out.get_program_sounds_state() == "active":
            if check_input():
                break

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
        Output.user_message_no_wait(confirmation_message)
        u_input = command_input()               # blocks, waiting for button input
        Output.stop_program_sounds()            # stop tts audio if still playing
        if u_input == 'A1': 
            pass                                # go on to the next step
        elif u_input == 'A2' or u_input == 'reset':
            Output.user_message('Cancelling')
            return                              # cancel function 
        # finally, execute the query
        try:
            app_nota.create_note(time, title, descriptor)
            Output.user_message('Note created!')
        except:
            Output.program_message('ERROR - cancelled create_full_note')
            Output.user_message('Error; something went wrong, note not created')

    # function to be used by notes output functions for creating tables
    ## must ensure that queries to the db use correct order of columns
    def output_result_table(result, table_title='a table'):
        table = Table(title=table_title, show_lines=True)
        # add a column to number the rows
        table.add_column('#', justify="center", no_wrap=True)
        # add columns for each note field
        table.add_column("Time", justify="left", style="dark_orange3", overflow='fold', min_width=20)
        table.add_column("Title", justify="left", style="cyan", overflow='fold', min_width=30)
        table.add_column("Descriptor", justify="left", style="cyan", overflow='fold', min_width=30)
        table.add_column("File Path", justify="left", style="wheat4", overflow='ellipsis', max_width=20)
        
        table_data = list(result)   # ensure result is a list
        # for audio output:
        ## get a list where each element is a string containing n notes (notes_per_page) at a time
        ## in other words, each element is like a *page*, and each page has at most n notes
        all_notes = ""
        current_page = 1
        notes_per_page = 10
        page_break = "[PAGE]"
        for n, note in enumerate(table_data):
            # add each note as table rows
            table.add_row(str(n+1), *note)         # the `*` works like it would passing arguments to a function - it unpacks the tuple (https://www.w3schools.com/python/python_tuples_unpack.asp)
            # get string for all notes (to be turned into pages)
            title = note[1]
            if n < (current_page*notes_per_page):
                all_notes += f"{n+1}: {title}. "
            else:
                all_notes += page_break
                all_notes += f"{n+1}: {title}. "
                current_page +=1
        note_pages = all_notes.split(page_break)
        # visual output - display the table
        io.visual_out.print_rich_table(table)
        # audio output - speak note titles
        ## read one page at a time, only moving on to the next page when the user provides correct input. Otherwise exit the function
        Output.user_message(f"Here is {table_title}")
        # add message to end of last page to let user know that there are no ore results
        note_pages[-1] += "End of search results. Press once to go through results again, or twice to exit"
        while True:
            for page in note_pages:
                io.audio_out.tts_speak(page)            # speak current page
                u_input = command_input()               # blocks, waiting for button input
                Output.stop_program_sounds()            # stop tts audio if still playing
                if u_input == 'A1':
                    pass                                # pass and read the next page 
                elif u_input == 'A2' or u_input == 'reset':
                    return                              # exit function

    def get_recent_notes(n=30):
        result = app_nota.get_recent_n_notes(n)
        AppNotesTasks.output_result_table(result, 'Recent Notes')

    def full_search(value:str):
        try:
            Output.program_message(f'(full_search) searching for "{value}"')
            matches = app_nota.get_sorted_notes_with_value(value)
            title = f"""Results for search: "{value}" """
            AppNotesTasks.output_result_table(matches, title)
        except:
            Output.program_message('ERROR - full search cancelled')
            Output.user_message('Error; something went wrong')
