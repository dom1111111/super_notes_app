"""
description incomplete
"""
import sqlite3

#--------------------------------#
# SQLite Database Setup

database_path = 'storage\main.db'

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

def create_note(time:str, title:str, descriptor:str=''):
    q = """
    INSERT INTO Notes (time, title, descriptor)
    VALUES(?, ?, ?);
    """
    q_values = (time, title, descriptor)
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
    return result

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
        note_descriptor = note[2].lower().split()
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
