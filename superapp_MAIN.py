import os
from time import sleep
from threading import Thread
from statistics import mode
from queue import SimpleQueue
import superapp_global_functions as funcs
# apps
import app_voice_memo


#--------------------#
# Voice commands

voice_command_map = {
    ('voice','memo'):app_voice_memo.create_memo,
    ('make','create','new','note','page'):lambda a : print('dummy command! +', a),
    ('make','create','new','task'):lambda a : print('dummy command! +', a)
    }

def voice_command():
    while True:
        while True:
            funcs.output_play_tone(1)   # play tone 1 to let user know that the voice command recording is starting
            funcs.input_record_start()  # start recording command audio
            # generate neccessary paths for the audio files
            folder = 'program_files'
            command_path = funcs.generate_file_path('command.wav', folder)
            content_path = funcs.generate_file_path('content.wav', folder)
            # collect command audio
            u_input = funcs.command_input()
            if u_input == 'A1' or u_input == 'A2':
                funcs.input_record_stop_and_write(command_path)
            elif u_input == 'reset':
                return  # cancel function 
            # start recording content audio
            funcs.input_record_start()
            # create thread to transcribe command audio in the mean time
            command_q = SimpleQueue()
            def command_transcribe():
                command_words = funcs.transcribe_audio_file(command_path)
                command_q.put(command_words)
            command_transcribe_thread = Thread(target=command_transcribe)
            command_transcribe_thread.daemon = True
            command_transcribe_thread.start()
            # collect content audio
            u_input = funcs.command_input()
            if u_input == 'A1' or u_input == 'A2':
                funcs.input_record_stop_and_write(content_path)
            elif u_input == 'reset':
                return  # cancel function     
            # transcribe content audio
            content = funcs.transcribe_audio_file(content_path)
            # now compare the command words against the map to see which command is the best match
            command = command_q.get()       # waits for the command transcription thread to do its thing (if needed)
            command_likelyness = []
            command_words = command.split()
            for keywords_tuple in voice_command_map.keys():
                for word in command_words:
                    if word in keywords_tuple:
                        command = voice_command_map.get(keywords_tuple)
                        command_likelyness.append(command)
            if command_likelyness:              # only do this if list is not empty
                command = mode(command_likelyness)  # get the command which shows up most often in the list (best match)
            else:
                funcs.output_tts('ERROR! Command not found, function cancelled')
                return
            # confirm with the user that the command is correct
            confirmation_message = f"executing {command.__name__} with the argument, {content}. Press once to confirm, and twice to start over"
            print(confirmation_message)
            funcs.output_tts(confirmation_message)
            u_input = funcs.command_input()
            if u_input == 'A1': 
                pass    # go on to the next step
            elif u_input == 'A2':
                break   # break the loop and start over
            elif u_input == 'reset':
                return  # cancel function 
            # finally, execute the command and exit out of the function
            command(content)
            return

#--------------------#
# Main

def startup():
    print()
    print('Starting Super Notes App...')

    script_path = os.path.realpath(__file__)        # gets the full file path of this script, including file name
    script_dir = os.path.dirname(script_path)       # gets the file path of this script, NOT including file name
    os.chdir(script_dir)                            # change cd to this scripts dir
    
    # send startup / welcome message to outcome


initial_commands_map = {
    'btnA*1':voice_command,               # start voice input
    'btnA*2':app_voice_memo.create_memo,  # default command
    'btnA*3':'',                          # reset / undo
    'btnA*4':'help',                      # help
    'btnA*10':exit                        # exit program
}

def main_loop():
    while True:
        print('accepting input...')
        input = funcs.get_input()                   # get input events
        command = initial_commands_map.get(input)   # compare them against the map of initial commands
        command()

#--------------------#

if __name__ == "__main__":
    startup()
    main_loop()










"""
TODO:

    you must have a large command map that outlines all of the commands
        
        ex: (all IO commands (ex: record, play, stop, output, etc.))

        and all app modules must use specific keywords to let this script know what they need,
        and it **all must be cleanly only coming from here!**

    add chimes sounds to each commands

"""

