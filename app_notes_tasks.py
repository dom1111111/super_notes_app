"""
description incomplete
"""
import sqlite3
from queue import SimpleQueue
from threading import Thread
import superapp_global_functions as funcs

#--------------------------------#
# SQLite Database Setup

database_folder_path = 'storage'
database_filename = 'main.db'

database_path = funcs.generate_file_path(database_filename, database_folder_path)

# connect to the databse (if it does not exist, it will create it)
sqlite_connection = sqlite3.connect(database_path)
con = sqlite_connection             # shortform
# create a cursor object once the connection has been established
cursor = sqlite_connection.cursor()
cur = cursor                        # shortform

#---

# Notes table setup
create_notes_table = """
CREATE TABLE IF NOT EXISTS Notes (
    time TEXT PRIMARY KEY,  -- created time. this is the main id
    title TEXT,             -- the title / main text content
    path TEXT,              -- related file/URL path
    descriptor TEXT         -- kewords to link this note to other notes
);
"""

cur.execute(create_notes_table)
con.commit()

#--------------------------------#

# a class for storing session info
class CurrentSession:
    def __init__(self):
        self.current_note = ''      # stores the id of the current page
        self.session_history = []   # stores the session's history of current pages
    def update_current_note(self, id):
        self.current_note = id
        # only append current note to history if it is different from the last
        if id != self.current_note:
            self.session_history.append(id)
    def reset_session(self):
        self.current_note = ''
        self.session_history.clear()

# instantiate the current session
session = CurrentSession()

#--------------------------------#
# Core Functions

# main function for querying the databse
def database_query(query, values=None):
    # description:
    """
    takes 2 arguments:
    * the first argument must be sqlite script and is always required
    * the second is optional, and is the values for script placeholders and MUST be a tuple (must include a `,`!)
    """
    if values:
        result = cur.execute(query, values)
    else:
        result = cur.execute(query)
    con.commit()    # Save (commit) the changes
    return result

    # also need code for error prevention

#---

def create_note(name:str):
    time = funcs.get_current_datetime_string()
    q = """
    INSERT INTO Notes (time, title)
    VALUES(?, ?);
    """
    q_values = (time, name)
    database_query(q, q_values)
    id = time
    session.update_current_note(id)

def edit_current_note_descriptor(descriptor:str):
    note = session.current_note
    q = """
    INSERT INTO Notes (descriptor)
    VALUES(?)
    WHERE WHERE time = ?;
    """
    q_values = (descriptor, note)
    database_query(q, q_values)

def edit_current_note_path(path:str):
    note = session.current_note
    q = """
    INSERT INTO Notes (path)
    VALUES(?)
    WHERE time = ?;
    """
    q_values = (path, note)
    database_query(q, q_values)

def get_specific_note(id):
    q = """
    SELECT time, title, path, descriptor FROM Notes
    WHERE time = ?;
    """
    q_values = (id,)
    result = database_query(q, q_values)
    session.update_current_note(id)
    return result

def get_last_50_notes():
    q = """
    SELECT time, title, descriptor, path FROM Notes
    ORDER BY time DESC
    LIMIT 50;
    """
    result = database_query(q)
    display_result_table(result)

# return list of notes whose titles contain the value
def get_notes_with_title_value(value:str):
    value_words = value.lower().split()
    # create the sqlite query with a WHERE / OR statement for each word in the value:
    q = """
    SELECT time, title, descriptor, path FROM Notes
    """
    for i, word in enumerate(value_words):  # allows to keep track of the current iteration of the for loop
        if i == 0:                          # only run this code if it's the fist item in the list
            q += """WHERE title LIKE ?"""
        else:
            q += """ OR title LIKE ?"""
    q += ";"
    # set up the query placeholder values to be each word in the value:
    q_values = []
    for word in value_words:
        q_values.append(f"%{word}%")
    q_values = tuple(q_values)
    # execute query:
    q_result = database_query(q, q_values)

    # now check to see which results match the search value best
    result_notes = []
    for note in q_result:                   # main cycle for each note from the query result
        word_match_count = 0
        note_title = note[1].lower().split()
        for note_word in note_title:        # cycle for each word in the title of each note
            for value_word in value_words:  # cycle for each word in the search value words
                if note_word == value_word:
                    word_match_count += 1   # if the note_word matches the value_word, increase the match count
        # now calculate the percentage of matched words in each note of the rersults
        match_percentage = (word_match_count / len(note_title)) * 100
        note_match = (match_percentage, note)
        result_notes.append(note_match)
    # finally, sort the results from highest match percentage to lowest and return
    sorted_result_notes = sorted(result_notes, reverse=True)
    final_result = [note[1] for note in sorted_result_notes]    # only return the notes, not the percentages
    return final_result

# return list of notes whose descriptors contain the value
def get_notes_with_descriptor_value(value:str):
    value_words = value.lower().split()
    # create the sqlite query with a WHERE / OR statement for each word in the value:
    q = """
    SELECT time, title, descriptor, path FROM Notes
    """
    for i, word in enumerate(value_words):  # allows to keep track of the current iteration of the for loop
        if i == 0:                          # only run this code if it's the fist item in the list
            q += """WHERE descriptor LIKE ?"""
        else:
            q += """ OR descriptor LIKE ?"""
    q += ";"
    # set up the query placeholder values to be each word in the value:
    q_values = []
    for word in value_words:
        q_values.append(f"%{word}%")
    q_values = tuple(q_values)
    # execute query:
    q_result = database_query(q, q_values)

    # now check to see which results match the search value best
    result_notes = []
    for note in q_result:                       # main cycle for each note from the query result
        word_match_count = 0
        note_descriptor = note[3].lower().split()
        for value_word in value_words:          # cycle for each word in the search value words
            for note_word in note_descriptor:   # cycle for each word in the title of each note
                if value_word == note_word:
                    word_match_count += 1       # if the note_word matches the value_word, increase the match count
        note_match = (word_match_count, note)
        result_notes.append(note_match)
    # finally, sort the results from highest match count to lowest and return
    sorted_result_notes = sorted(result_notes, reverse=True)
    final_result = [note[1] for note in sorted_result_notes]    # only return the notes, not the match number
    return final_result


# TODO:
    # the desciptor can be the same as above but reversed
        # matches the percentage for the result descriptor matching the search value (do the vice versa of above)




#--------------------------------#

# Combo Functions
    # these functions use the Core functions and superapp_global_functions to work


# function to be used by output functions for creating tables
## must ensure that queries to the db use this order or columns
def display_result_table(result):
    table_data = list(result)
    column_names = ('Time', 'Title', 'Descriptor', 'File Path')
    table_data.insert(0, column_names)
    funcs.output_do_visual_function('print_notes_table', table_data)


def create_full_voice_note():
    funcs.output_play_tone(1)
    # start recording title audio
    funcs.input_record_start()

    # create path for the note's associated audio files
    time = funcs.get_current_datetime_string()
    folder_path = funcs.generate_file_path('files', 'storage')
    title_id = time + '_title.wav'
    title_file_path = funcs.generate_file_path(title_id, folder_path)
    descriptor_id = time + '_descriptor.wav'
    descriptor_file_path = funcs.generate_file_path(descriptor_id, folder_path)

    # end recording for title
    u_input = funcs.command_input()
    if u_input == 'A1' or u_input == 'A2':
        funcs.input_record_stop_and_write(title_file_path)
    elif u_input == 'reset':
        funcs.input_record_stop()
        return                              # exit function
    
    # start recording descriptor audio
    funcs.input_record_start()
    
    # create thread to transcribe title audio in the mean time
    title_q = SimpleQueue()
    def title_transcribe():
        title_text = funcs.transcribe_audio_file(title_file_path)
        title_q.put(title_text)
    command_transcribe_thread = Thread(target=title_transcribe)
    command_transcribe_thread.daemon = True
    command_transcribe_thread.start()
    
    # end recording for descriptor
    u_input = funcs.command_input()
    if u_input == 'A1' or u_input == 'A2':
        funcs.input_record_stop_and_write(descriptor_file_path)
    elif u_input == 'reset':
        funcs.input_record_stop()
        return                              # exit function 

    # transcribe descriptor audio
    descriptor = funcs.transcribe_audio_file(descriptor_file_path)
    
    # waits for the title transcription thread to do its thing (if needed)
    title = title_q.get()                   

    # confirm with the user that the input is correct
    confirmation_message = f"""creating note with title: "{title}", and descriptor: "{descriptor}". Press once to confirm, and twice or more to cancel"""
    funcs.output_do_visual_function('print_user_message', confirmation_message)
    funcs.output_tts(confirmation_message)
    u_input = funcs.command_input()         # blocks, waiting for button input
    funcs.stop_program_sounds()             # stop tts audio if still playing
    if u_input == 'A1': 
        pass                                # go on to the next step
    elif u_input == 'reset':
        return                              # cancel function 
    # finally, execute the query
    path = title_file_path + ', ' + descriptor_file_path
    q = """
    INSERT INTO Notes (time, title, path, descriptor)
    VALUES(?, ?, ?, ?);
    """
    q_values = (time, title, path, descriptor)
    database_query(q, q_values)
    id = time
    session.update_current_note(id)


def full_search(value:str):
    title_matches = get_notes_with_title_value(value)
    descriptor_matches = get_notes_with_descriptor_value(value)
    all_matches = title_matches + descriptor_matches
    # delete duplicates?
    
    display_result_table(all_matches)




# TODO:
# test new descriptor sorting function
# test combo functions



# NOTES:
"""
create task (by name)

VIEW - return task to be read or viewed - render all child and parent tasks
(for read, only do names)

return name and timestamp id of current task

functions for giving the task meta data


today's tasks - generate the tasks for today


undo last command
"""

# this will handle
    # alarm
    # creating and sorting tasks
    # automatic task deligation
    # etc.


# testing
"""
table = cur.execute("SELECT * FROM Notes;")

for row in table:
    print(row)
"""

"""
while True:
    print()
    ui = input('tpye: ')
    full_search(ui)
"""