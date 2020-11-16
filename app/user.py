# user.py: user logging, creation, edits, delete

import os, rich

def student_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists students(AdmnNO char(6) NOT NULL, Name varchar(255) NOT NULL, Class char(2) NOT NULL, Stream varchar(4) NOT NULL, PRIMARY KEY (AdmnNO));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = 'bruh'
    try:
        cursor.execute(query)
        to_print = '[CREATE] TABLE STUDENT'
    except Exception:
        console.print(':bulb: Existing student table found ')
        to_print = '[DB ERROR]: EXISTING TABLE FOUND'

    with open(LOG_PATH, 'a') as log_file:
        log_file.write(to_print+'\n')

def exists(admmno):
    console = rich.console.Console()
