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

def create_note(time:str, title:str, descriptor:str=None):
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

def get_recent_n_notes(n):
    q = """
    SELECT time, title, descriptor, path FROM Notes
    ORDER BY time DESC
    LIMIT ?;
    """
    q_values = (n,)
    result = database_query(q, q_values)
    return result

# return list of notes whose column field contain the value
def get_notes_with_column_value(column_name, value:str):
    value_words = value.lower().split()
    # create the sqlite query with a WHERE / OR statement for each word in the value:
    q = """
    SELECT time, title, descriptor, path FROM Notes
    """
    ## adjust the query dpepending on the column_name given
    if column_name == 'title':
        for i, word in enumerate(value_words):  # allows to keep track of the current iteration of the for loop
            if i == 0:                          # only run this code if it's the fist item in the list
                q += """WHERE title LIKE ?"""
            else:
                q += """ OR title LIKE ?"""
        q += ";"
    elif column_name == 'descriptor':
        for i, word in enumerate(value_words):
            if i == 0:
                q += """WHERE descriptor LIKE ?"""
            else:
                q += """ OR descriptor LIKE ?"""
        q += ";"
    else:
        # cancel function
        return
    # set up the query placeholder values to be each word in the value:
    q_values = []
    for word in value_words:
        q_values.append(f"%{word}%")
    q_values = tuple(q_values)
    # execute query:
    q_result = database_query(q, q_values)
    return q_result

# get notes whose title and descriptor fields match the value and order them by best match
def get_sorted_notes_with_value(value):
    title_matches = list(get_notes_with_column_value('title', value))
    descriptor_matches = list(get_notes_with_column_value('descriptor', value))
    all_matches = title_matches + descriptor_matches
    # remove duplicates by converting list to dict and then back to list
    all_matches = list(dict.fromkeys(all_matches))

    # process the matches list in several steps to order the notes from best match to least
    value_words = value.lower().split()         # make sure the value is all lowercase, and split string into a list of words
    value_word_count = len(value_words)
    ## 1) find number of times a note's title or descriptor contains the value, or contains a part of the value with the words still in order
    numbered_matches = []
    match_numbers = []
    # main loop cycle for each note
    for note in all_matches:                    
        title = note[1].lower()
        if note[2]:
            descriptor = note[2].lower()
        else:
            descriptor = ''
        title_match_count = 0
        descriptor_match_count = 0
        # the loop cycle to build every partial version of the value while still keeping the words in order
        for n1 in range(value_word_count):      # cycle for starting word index, from first word to last
            for n in range(value_word_count):   # the cycle to get the ending word index - must come after the starting word
                high_index = value_word_count - n
                if high_index > n1:
                    value_part = ' '.join(value_words[n1:high_index])
                    # print(n1, high_index, '->', value_part)
                    if value_part in title:
                        title_match_count += 1
                    if value_part in descriptor:
                        descriptor_match_count += 1
        # add a tutple with each note's match numbers along with the note itself to the ordered match list 
        numbered_matches.append((title_match_count, descriptor_match_count, note))
        match_numbers.extend((title_match_count, descriptor_match_count))
    ## 2) sort the matches list by most point to least points
    ### when title has the same points as descriptor, put title first
    #### when there are multiple titles with the same points, titles are sorted by percentage of their words that are matches
    ordered_matched_notes = []
    # sort match_numbers from highest to lowest, delete duplicates, and remove 0
    ordered_match_numbers = sorted(match_numbers, reverse=True)
    ordered_match_numbers = list(dict.fromkeys(ordered_match_numbers))
    ordered_match_numbers.pop(ordered_match_numbers.index(0))
    # iterate through ordered_numbers, adding notes to ordered_matched_notes using the ordering rules on each cycle 
    for n in ordered_match_numbers:
        title_n_matches = []
        descriptor_n_matches = []
        for note in numbered_matches:
            # a) first find notes whose titles are equal to n (the match number)
            if note[0] == n:
                title_n_matches.append(note[2])     # only add the note itself (note[2]), not the match numbers
            # b) then find notes whose descriptors are equal to n    
            if note[1] == n:
                descriptor_n_matches.append(note[2])
        sorted_title_n_matches = []
        for match in title_n_matches:
            title_words = match[1].lower().split()  # get the note's title words
            single_word_match_count = 0
            # increase the word match count if the title word matches the value word
            for word1 in value_words:
                for word2 in title_words:
                    if word1 == word2:
                        single_word_match_count += 1
            # compare the number of matched title words to the total number of title words, and get percentage
            percentage = (single_word_match_count / len(title_words)) * 100

            sorted_title_n_matches.append((percentage, match))
        sorted_title_n_matches = sorted(sorted_title_n_matches, reverse=True)
        # now add title matched notes followed by desriptor matched notes
        ordered_matched_notes.extend(note[1] for note in sorted_title_n_matches) # only get the notes without the percentage)
        ordered_matched_notes.extend(descriptor_n_matches)
    # return the final result
    return ordered_matched_notes








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
