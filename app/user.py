# user.py: user logging, creation, edits, delete

import os, rich
from PyInquirer import prompt

def student_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists students(AdmnNO char(6) NOT NULL, Name varchar(255) NOT NULL, Class char(3) NOT NULL, Stream varchar(5) NOT NULL, PSWDHASH CHAR(60) NOT NULL, PRIMARY KEY (AdmnNO));"
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

def exists(cursor, admmno):
    try:
        cursor.execute('select * from students where AdmnNO = {};'.format(admmno.upper()))
        return True
    except Exception:
        return False

def student_create_prompt(cursor, admnno, pswd_hash):
    console = rich.console.Console()
    console.print('🆕 [b green] New Student Registration Form [/b green]\n')
    questions = [
        {
            'type': 'input',
            'name': 'full_name',
            'message': 'What\'s your name',
        },
        {
            'type': 'input',
            'name': 'clsec',
            'message': 'What\'s your class and section',
            'default': '12I'
        },
        {
            'type': 'list',
            'name': 'stream',
            'message': 'What\'s your stream ?',
            'choices': ['PCB', 'PCMC', 'PCMB', 'PCME', 'COMM.', 'HUMA.', 'OTHER'],
        },
    ]
    answers = prompt(questions)
    if answers['stream'] == 'OTHER':
        other_stream = str(input('Enter other stream (5 letters): '))
        answers['stream'] = other_stream
    print(admnno, pswd_hash, answers)