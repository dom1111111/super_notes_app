import superapp_global_functions as funcs
import os

#--------------------#

def generate_timestamp_file_path():
    time = funcs.get_current_datetime_string_filename_safe()
    filename = f"{time}.wav"
    foldername = 'recordings'
    path = funcs.generate_file_path(filename, foldername)
    return path

def create_memo():
    path = generate_timestamp_file_path()
    funcs.full_record(path)




"""
functions of voice memo

* record audio
* keep a record of all audio files by file_path
* scroll through audio files (up and down) and play them
* be able to stop, pause/resume audio files as well
"""