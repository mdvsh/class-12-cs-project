# user.py: user logging, creation, edits, delete

import os


def student_create_table(cursor):
    query = "create table students(AdmnNO char(6) NOT NULL, Name varchar(255) NOT NULL, Class char(2) NOT NULL, Stream varchar(4) NOT NULL, PRIMARY KEY (AdmnNO));"
    try:
        cursor.execute(query)
        to_print = '[CREATE] TABLE STUDENT: COMMAND'
        this_dir, this_filename = os.path.split(__file__)
        DATA_PATH = os.path.join(this_dir, "logs", "logs.txt")
        with open(DATA_PATH, 'a') as log_file:
            log_file.write(to_print)
    except Exception as e:
        if hasattr(e, 'message'):
            print('[DB ERROR]:', e.message)
        else:
            print('[DB ERROR]:', e)
