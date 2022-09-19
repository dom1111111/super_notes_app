"""
description incomplete
"""
import sqlite3
import os
from datetime import datetime

#--------------------------------#
# SQLite Database Setup

database_filename = 'main.db'  # pages.db

script_path = os.path.realpath(__file__)        # gets the full file path of this script, including file name
script_dir = os.path.dirname(script_path)       # gets the file path of this script, NOT including file name
database_path = os.path.join(script_dir, database_filename) # join the script file path with directory name
# os.chdir(script_dir)                          # change current directory to the scripts directory

# connect to the databse (if it does not exist, it will create it)
sqlite_connection = sqlite3.connect(database_path)
con = sqlite_connection             # shortform
# create a cursor object once the connection has been established
cursor = sqlite_connection.cursor() # shortform
cur = cursor   

#---

# Tasks table setup
create_tasks_table_q = """
CREATE TABLE IF NOT EXISTS Tasks (
    time TEXT PRIMARY KEY,  -- created time. this is the main id
    name TEXT,
    audio TEXT,             -- a string of a file path refferencing the audio file
    parent_tasks,
    child_tasks,
    do_date TEXT,           
    importance INTEGER,     -- should only be 1, 2, 3, or 4
    recurrence TEXT,
    status TEXT,
    finished_time TEXT      -- to store when the tasks was marked as finished
);
"""

# Notes table setup
create_notes_table_q = """
CREATE TABLE IF NOT EXISTS Notes (
    time TEXT PRIMARY KEY,  -- created time. this is the main id
    name TEXT,
    audio TEXT,             -- a string of a file path refferencing the audio file
    sub_content TEXT,       -- to store serialized text documents
    parent_notes,
    child_notes,
);
"""

# Projects table setup
create_projects_table_q = """
CREATE TABLE IF NOT EXISTS Projects (
    name TEXT PRIMARY KEY,
    parent_projects TEXT,
    child_projects TEXT,
    task_links TEXT,
    note_links TEXT
);
"""

cur.execute(create_tasks_table_q)
cur.execute(create_notes_table_q)
cur.execute(create_projects_table_q)
con.commit()

#--------------------------------#
# Supporting Functions & Setup

class CurrentSession:
    def __init__(self):
        self.current_page = ''      # stores the id of the current page
        self.session_history = []   # stores the session's history of current pages
    def update_current_page(self, id):
        self.current_page = id
    def update_session_history(self, id):
        self.session_history.append(id)
    def reset_session(self):
        self.current_page = ''
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

def get_current_datetime_string():
    now = datetime.now()
    datetime_string = now.strftime('%Y-%m-%d_%H:%M:%S')
    return datetime_string

#--------------------------------#

# instantiate the crrent session
this_session = CurrentSession()

#--------------------------------#
# Main Functions

def create_task(name, recording_filepath=None):
    time = get_current_datetime_string()
    q = """
    INSERT INTO Tasks (time, name, audio)
    VALUES(?, ?, ?);
    """
    q_values = (time, name, recording_filepath)
    database_query(q, q_values)
    task_id = time
    this_session.update_current_page(task_id)

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

create_task("get up and dance!")

table = database_query("SELECT * FROM Tasks")

for row in table:
    print(row)

