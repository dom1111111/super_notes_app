import os
from time import sleep
from datetime import datetime
from statistics import mode
import superapp_global_functions as funcs

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
    funcs.Output.user_message(message)
    exit()

#--------------------#
# misc functions/commands

def tell_current_time():
    now = datetime.now()
    time = now.strftime('%I:%M %p')
    message = f"It is currently: {time}"
    funcs.Output.user_message(message)

def tell_current_date():
    now = datetime.now()
    weekday = now.strftime('%A')
    date = now.strftime('%B %d')
    if weekday == 'Wednesday':
        message = f"It is {weekday} my dudes, {date}"
    else:
        message = f"It is {weekday}, {date}"
    funcs.Output.user_message(message)

#--------------------#
# Voice command

def find_command_from_words(command_words:list):
    # turn the command into a set of words
    command_words = set(command_words)
    # these are variables representing each keyword and their synonyms
    ## they are True if any command words are present in their sets
    get = not command_words.isdisjoint({'get', 'return', 'retrieve', 'show', 'display', 'read'})
    search = not command_words.isdisjoint({'search', 'find', 'seek', 'look'})
    create = not command_words.isdisjoint({'create','make','new'})
    recent = not command_words.isdisjoint({'recent', 'latest', 'last'})
    current = not command_words.isdisjoint({'current', 'present'})
    today = not command_words.isdisjoint({'today', 'todays', "today's"})
    note = not command_words.isdisjoint({'note', 'notes', 'page'})
    task = not command_words.isdisjoint({'task', 'todo', 'to-do'})
    exit = not command_words.isdisjoint({'exit', 'bye', 'goodbye'})
    # a function to see if individual words are in the set
    def is_word_in_command(word):
        return True if word in command_words else False
    # a list of commands and their keyword requirements
    commands = [
        (funcs.AppNotesTasks.create_full_note, (create and note)),
        #(funcs.AppNotesTasks.create_full_task, (create and task)),
        (funcs.AppNotesTasks.full_search, (search and note)),
        (funcs.AppNotesTasks.get_recent_notes, (recent and note)),
        (tell_current_time, ((current or is_word_in_command('now')) and is_word_in_command('time'))),
        (tell_current_date, ((current or today) and is_word_in_command('date'))),
        (shutdown, (exit))
    ]
    # now return the command whose requirement is met 
    for command, requirement in commands:
        if requirement:
            return command

def voice_command():
    # 1) collect audio
    funcs.Output.play_tone(1)               # play tone 1 to let user know that the voice command recording is starting
    funcs.AudioRec.start()                  # start recording command audio
    ## generate neccessary paths for the audio files
    folder = 'program_files'
    audio_path = funcs.generate_file_path('voice_command.wav', folder)
    ## collect command audio
    u_input = funcs.command_input()
    if u_input == 'A1' or u_input == 'A2':
        funcs.AudioRec.stop_and_write(audio_path)
    elif u_input == 'reset':
        funcs.AudioRec.stop()
        return                              # exit function      
    ## transcribe audio
    funcs.Output.play_tone(2)               # lets user know the audio was recieved
    funcs.Output.program_message("processing audio...")
    audio_text = funcs.transcribe_audio_file(audio_path)
    funcs.Output.program_message(f"""understood audio as "{audio_text}" """)
    # 2) split the audio text into comand and content according to one of the split words
    try: # only do this if audio text is properly returned
        audio_text_words = audio_text.split()
        audio_text_words_lower = audio_text.lower().split()
    except:
        return
    split_words = ("content", "stuff")
    ## only do this if a split word is present (not all commands require splitting for arguments)
    # finds the first instance of a split word - any words coming after are ignored for splitting 
    for word in audio_text_words_lower:
        if word in split_words:
            split_index = audio_text_words.index(word)
            ## seperate text into command and content
            command_words = audio_text_words[0:split_index]
            content_words = audio_text_words[split_index+1:]
            content = ' '.join(content_words)
            break
        else:
            command_words = audio_text_words
            content = ''
    # 3) compare the command words against the map to see which command is the best match
    command = find_command_from_words(command_words)
    # 4) finally, execute the command with content as an argument, but only if there is content 
    command(content) if content else command()

#--------------------#
# Main

def main_loop():
    initial_commands_map = {
        'btnA*1':voice_command,                         # start voice input
        'btnA*2':funcs.AppNotesTasks.quick_memo,        # default command
        'btnA*3':'',                                    # reset / undo
        'btnA*4':'help',                                # help
        'btnA*10':shutdown                              # exit program
    }
    while True:
        print()
        funcs.Output.user_message_no_wait("Home Base")
        input = funcs.get_input()                   # get input events
        command = initial_commands_map.get(input)   # compare them against the map of initial commands
        print()
        command()

#--------------------#

if __name__ == "__main__":
    startup()
    main_loop()
