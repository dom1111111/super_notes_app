import os
from time import sleep
from datetime import datetime
from statistics import mode
import superapp_global_functions as funcs
# apps
import app_notes_tasks

#--------------------#
# program functions

def startup():
    print()
    print('Starting Super Notes App...')

    script_path = os.path.realpath(__file__)        # gets the full file path of this script, including file name
    script_dir = os.path.dirname(script_path)       # gets the file path of this script, NOT including file name
    os.chdir(script_dir)                            # change cd to this scripts dir
    
    # send startup / welcome message to outcome

def shutdown():
    message = "goodbye!"
    funcs.output_do_visual_function('print_user_message', message)
    funcs.output_tts(message)
    sleep(2)
    exit()

#--------------------#
# misc functions/commands

def tell_current_time():
    now = datetime.now()
    time = now.strftime('%I:%M %p')
    message = f"It is currently: {time}"
    funcs.output_do_visual_function('print_user_message', message)
    funcs.output_tts(message)

def tell_current_date():
    now = datetime.now()
    weekday = now.strftime('%A')
    date = now.strftime('%B %d')
    if weekday == 'Wednesday':
        message = f"It is {weekday} my dudes, {date}"
    else:
        message = f"It is {weekday}, {date}"
    funcs.output_do_visual_function('print_user_message', message)
    funcs.output_tts(message)

#--------------------#
# Voice commands

voice_command_map = {
    ('make','create','new','note','page'):lambda a : print('dummy command! +', a),
    ('make','create','new','task'):lambda a : print('dummy command! +', a),
    ('find', 'search', 'get', 'retrieve', 'show', 'note', 'notes', 'page'):app_notes_tasks.full_search,
    ('get', 'show', 'return', 'display', 'read', 'last', 'recent', 'note', 'notes'):app_notes_tasks.get_last_50_notes,
    ('exit', 'bye', 'goodbye', 'program', 'application'):shutdown,
    ('say', 'speak', 'tell', 'get', 'display', 'what', 'current', 'time'):tell_current_time,
    ('say', 'speak', 'tell', 'get', 'display', 'what', 'current', 'date', 'today', 'todays', "today's"):tell_current_date
    }

def voice_command():
    # while True:
    #   while True:

    # 1) collect audio
    funcs.output_play_tone(1)               # play tone 1 to let user know that the voice command recording is starting
    funcs.input_record_start()              # start recording command audio
    ## generate neccessary paths for the audio files
    folder = 'program_files'
    audio_path = funcs.generate_file_path('voice_command.wav', folder)
    ## collect command audio
    u_input = funcs.command_input()
    if u_input == 'A1' or u_input == 'A2':
        funcs.input_record_stop_and_write(audio_path)
    elif u_input == 'reset':
        funcs.input_record_stop()
        return                              # exit function      
    ## transcribe audio
    funcs.output_play_tone(2)               # lets user know the audio was recieved
    funcs.output_do_visual_function('print_program_message', "processing audio...")
    audio_text = funcs.transcribe_audio_file(audio_path)

    # 2) split the audio text into comand and content according to one of the split words
    try: # only do this if audio text is properly returned
        audio_text_words = audio_text.split()
    except:
        return
    split_word = "content"
    ## only do this if the split word is present (not all commands require splitting for arguments)
    if split_word in audio_text_words:
        split_index = audio_text_words.index(split_word)
        ## seperate text into command and content
        command_words = audio_text_words[0:split_index]
        content_words = audio_text_words[split_index+1:]
        content = ' '.join(content_words)
    else:
        command_words = audio_text_words
        content = ''
    # 3) compare the command words against the map to see which command is the best match
    command_likelyness = []
    for keywords_tuple in voice_command_map.keys():
        for word in command_words:
            if word in keywords_tuple:
                command = voice_command_map.get(keywords_tuple)
                command_likelyness.append(command)
    if command_likelyness:                  # only do this if list is not empty
        command = mode(command_likelyness)  # get the command which shows up most often in the list (best match)
    else:
        funcs.output_tts('ERROR! Command not found, function cancelled')
        return
    # 4) confirm with the user that the command is correct
    confirmation_message = f"executing: {command.__name__}, with the argument: {content}. Press once to confirm, and twice to start over"
    funcs.output_do_visual_function('print_user_message', confirmation_message)
    funcs.output_tts(confirmation_message)
    u_input = funcs.command_input()         # blocks, waiting for button input
    funcs.stop_program_sounds()             # stop tts audio if still playing
    if u_input == 'A1':
        pass                                # go on to the next step
    elif u_input == 'A2':
        return # break                      # break the loop and start over
    elif u_input == 'reset':
        return                              # cancel function 
    # 5) finally, execute the command
    if content:
        command(content)
    else:
        command()
    return

#--------------------#
# Main

def main_loop():
    initial_commands_map = {
        'btnA*1':voice_command,                         # start voice input
        'btnA*2':app_notes_tasks.create_full_voice_note,# default command
        'btnA*3':'',                                    # reset / undo
        'btnA*4':'help',                                # help
        'btnA*10':shutdown                              # exit program
    }
    while True:
        print()
        funcs.output_do_visual_function('print_program_message', 'accepting input')
        input = funcs.get_input()                   # get input events
        command = initial_commands_map.get(input)   # compare them against the map of initial commands
        print()
        command()

#--------------------#

if __name__ == "__main__":
    startup()
    main_loop()
