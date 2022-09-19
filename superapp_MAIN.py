import os
from time import sleep
import superapp_global_functions as funcs
from threading import Thread
from statistics import mode

# apps
import app_voice_memo


#--------------------#
# Voice commands

voice_command_map = {
    ('voice', 'memo',):app_voice_memo.create_memo,
    }

def voice_command():
    loop = True
    while loop:
        # start recording command audio
        funcs.record_start()
        # generate neccessary paths for the audio files
        folder = 'temp_audio'
        command_path = funcs.generate_file_path('command.wav', folder)
        content_path = funcs.generate_file_path('content.wav', folder)
        # collect command audio
        input = funcs.check_input()
        if input == 'bA_1' or input == 'bA_2':
            funcs.record_stop_and_write(command_path)
        elif input == 'reset':
            return  # cancel function 
        # start recording content audio
        funcs.record_start()
        # create thread to transcribe command audio in the mean time
        command_words_container = []
        def command_transcribe():
            command_words = funcs.transcribe_audio_file(command_path)
            command_words_container.append(command_words)
        command_transcribe_thread = Thread(target=command_transcribe)
        command_transcribe_thread.daemon = True
        command_transcribe_thread.start()
        # collect content audio
        input = funcs.check_input()
        if input == 'bA_1' or input == 'bA_2':
            funcs.record_stop_and_write(content_path)
        elif input == 'reset':
            return  # cancel function     
        # transcribe audio and do a command
        command = command_words_container[0]
        content = funcs.transcribe_audio_file(content_path)
        # now compare the command words against the map to see which command is the best match
        command_likelyness = []
        for keywords_tuple in voice_command_map.keys():
            for word in command.split():
                if word in keywords_tuple:
                    command = voice_command_map.get(keywords_tuple)
                    command_likelyness.append(command)
        if command_likelyness:              # only do this is list is not empty
            command = mode(command_likelyness)  # get the command which shows up most often in the list (best match)
        else:
            funcs.tts('ERROR! command not found')
            return
        # confirm with the user that the command is correct
        funcs.tts(f"executing {command.__name__} with ")
        # single press is yes, double is no
    # finally, execute the command
    command(content)


#--------------------#
# Main

def startup():
    print()
    print('Starting Super Notes App...')

    script_path = os.path.realpath(__file__)        # gets the full file path of this script, including file name
    script_dir = os.path.dirname(script_path)       # gets the file path of this script, NOT including file name
    os.chdir(script_dir)                            # change cd to this scripts dir
    
    # send startup / welcome message to outcome

def main_loop():
    map = {
        'bA_1':voice_command,               # start voice input
        'bA_2':app_voice_memo.create_memo,  # default command
        'bA_3':'',                          # reset / undo
        'bA_4':'help',                      # help
        'bA_10':exit                        # exit program
    }
    while True:
        input = funcs.get_input()           # get input events
        command = map.get(input)            # compare them against the map of initial commands
        command()


if __name__ == "__main__":
    startup()
    main_loop()


"""
so here's the loop

main_primary_thread     wait for input
IO                      input event happens and is sent to input queue
main_primary_thread     get input from input queue and do something with it
main_primary_thread     call function in apps
app                     process stuff, send command requests to main
main_secondary_thread   get command request (each with proper dictionary format)
main_secondary_thread   call main functions to process command
main_secondary_thread   return result to app queue
app                     either repeat the above, or finish stuff and return to main
main                    the full cycle has completed, go back to beginning

"""


#--------------------#

"""
TODO:

    you must have a large command map that outlines all of the commands
        
        ex: (all IO commands (ex: record, play, stop, output, etc.))

        and all app modules must use specific keywords to let this script know what they need,
        and it **all must be cleanly only coming from here!**

    add chimes sounds to each commands

"""

