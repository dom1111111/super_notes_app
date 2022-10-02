"""
description incomplete
"""
import sqlite3
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
# Supporting Functions & Setup

class CurrentSession:
    def __init__(self):
        self.current_note = ''      # stores the id of the current page
        self.session_history = []   # stores the session's history of current pages
    def update_current_note(self, id):
        self.current_note = id
    def update_session_history(self, id):
        self.session_history.append(id)
    def reset_session(self):
        self.current_note = ''
        self.session_history.clear()

# main function for querying the databse
def database_query(query, values=None):
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

#--------------------------------#

# instantiate the current session
this_session = CurrentSession()

#--------------------------------#
# Core Basic Functions

def create_note(name):
    time = funcs.get_current_datetime_string()
    q = """
    INSERT INTO Notes (time, title)
    VALUES(?, ?);
    """
    q_values = (time, name)
    database_query(q, q_values)
    id = time
    this_session.update_current_note(id)

def edit_current_note_descriptor(descriptor):
    note = this_session.current_note
    q = """
    INSERT INTO Notes (descriptor)
    VALUES(?)
    WHERE WHERE time = ?;
    """
    q_values = (descriptor, note)
    database_query(q, q_values)

def get_specific_note(id):
    q = """
    SELECT time, title, path, descriptor FROM Notes
    WHERE time = ?;
    """
    q_values = (id,)
    result = database_query(q, q_values)
    this_session.update_current_note(id)
    return result

# return notes whose titles contain the value
def get_notes_with_title_value(value):
    value_words = value.lower().split()
    # create the sqlite query with a WHERE / OR statement for each word in the value:
    q = """
    SELECT time, title, path, descriptor FROM Notes
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
        for note_word in note_title:  # cycle for each word in the title of each note
            for word in value_words:        # cycle for each word in the search value words
                if note_word == word:
                    word_match_count += 1   # if the note_word matches the value_word, increase the match count
        # now calculate the percentage of matched words in each note of the rersults
        match_percentage = (word_match_count / len(note_title)) * 100
        note_match = (match_percentage, note)
        result_notes.append(note_match)
    # finally, sort the results from highest match percentage to lowest and return
    sorted_result_notes = sorted(result_notes, reverse=True)
    return sorted_result_notes






# TODO:
    # the desciptor can be the same as above but reversed
        # matches the percentage for the result descriptor matching the search value (do the vice versa of above)


# return notes whose descriptors contain the value
def get_notes_with_descriptor_value(value):
    q = """
    SELECT time, title, path, descriptor FROM Notes
    WHERE descriptor LIKE ?;
    """
    q_values = (f'%{value}%',)
    result = database_query(q, q_values)
    return result


#--------------------------------#

# these next functions are not core, but specific to viewing notes/generating views

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




#--------------------------------#
#########
#########
# testing

print('hi!')

# create_note("four men go to the bank bitch!")

"""
val = ("%four%",)

table = database_query("SELECT * FROM Notes WHERE title LIKE ?;", val)

for row in table:
    print(row)
"""


while True:
    i = input("search in notes: ")
    table = get_notes_with_title_value(i)
    for row in table:
        print(row)

