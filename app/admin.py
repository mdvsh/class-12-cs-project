# user.py: user logging, creation, edits, delete

import os, rich
from PyInquirer import prompt
import mysql.connector as mysql

def teacher_create_table(cursor):
    console = rich.console.Console()
    query = "CREATE TABLE IF NOT EXISTS teachers (TrNO CHAR(6) NOT NULL, Name VARCHAR(255) NOT NULL, IS_COUNSELOR BOOLEAN NOT NULL, Subject VARCHAR(15), PSWDHASH CHAR(60) NOT NULL, PRIMARY KEY (TrNO));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = 'bruh'
    try:
        cursor.execute(query)
        to_print = '[CREATE] TABLE TEACHER'
    except Exception:
        console.print(':bulb: Existing teacher table found ')
        to_print = '[DB ERROR]: EXISTING TABLE FOUND'

    with open(LOG_PATH, 'a') as log_file:
        log_file.write(to_print+'\n')

def exists(cursor, trno):
    global exists
    exists = False
    cursor.execute("select * from teachers where TrNO='{}';".format(trno))
    output = cursor.fetchone()
    # print(output)
    if output != None:
        exists = True
    return exists

def get_pswdhash(cursor, trno):
    trno = trno.upper()
    cursor.execute("select PSWDHASH from students where TrNO='{}';".format(trno))
    output = cursor.fetchone()
    return output[0].encode('ascii')

def teacher_create_prompt(db, cursor, trno, pswd_hash):
    trno = trno.upper()
    console = rich.console.Console()
    table = rich.table.Table(show_header=True, header_style="bold magenta", show_footer=False)
    console.print('🆕 [bold green] New Teacher Registration Form [/bold green]\n')
    questions = [
        {
            'type': 'input',
            'name': 'full_name',
            'message': 'What\'s your name',
        },
        {
        
            'type': 'confirm',
            'name': 'is_counselor',
            'message': 'Are you the counselor?',
            'default': False
        },
        {
            'type': 'list',
            'name': 'subject',
            'message': 'What subject do you teach?',
            'choices': ['Accountancy', 'Biology', 'Biotechnology', 'BusinessStudies', 'Chemistry', 'ComputerScience', 'Economics', 'English', 'FineArts', 'Geography', 'Hindi', 'Mathematics', 'PerformingArts', 'PE', 'Physics', 'Political Science', 'Sanskrit' 'French', 'German'],
            'when': lambda answers: not answers['is_counselor']
        },
    ]
    answers = prompt(questions)
    
    if not answers["is_counselor"]:
        # print(trno, pswd_hash, answers)
        query = "insert into teachers values ('{}', '{}', {}, '{}', '{}');".format(trno, answers['full_name'], answers['is_counselor'], answers['subject'], pswd_hash)
    
    else:
        query = "insert into teachers values ('{}', '{}', {}, {}, '{}');".format(trno, answers['full_name'], answers['is_counselor'], 'NULL', pswd_hash)

    table.add_column("Tr. No.")
    table.add_column('Teacher Name', width=18)
    table.add_column("Counselor?", justify='center')
    table.add_column("Subject", justify='center')
    table.add_column("Additional Info.", justify='left')
    
    if not answers["is_counselor"]:
        table.add_row(
            f'[bold]{trno}[/]',
            f'{answers["full_name"]}',
            f'{answers["is_counselor"]}',
            f'{answers["subject"]}',
            "Your password is hashed securely with bcrypt."
        )
    else:
        table.add_row(
            f'[bold]{trno}[/]',
            f'{answers["full_name"]}',
            f'{answers["is_counselor"]}',
            'None',
            "Your password is hashed securely with bcrypt."
        )

    console.print("\n\n[yellow]Here's what we got from you[/]\n", table)

    # inquirer to confrim user details before adding
    confirm = [
        {'type': 'confirm', 'message': 'Are all the details correct?', 'name': 'verify', 'default': True},
        {'type': 'confirm', 'message': 'Finish registration?', 'name': 'finish', 'default': True}
    ]

    confirmation = prompt(confirm)

    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = 'bruh'
    global ok
    ok = False

    if confirmation['verify'] and confirmation['finish']:
        try:
            cursor.execute(query)
            to_print = '[INSERT] NEW ROW TEACHER'
            db.commit()
            ok = True
        except mysql.Error as e:
            console.print('⚠️ Something Went Wrong :-(')
            to_print = f'[DB ERROR]: INSERTING\nMessage: {e}'
    else:
       console.print('[blink][i]Oopsie wOOpsiee...[/i]\n\nOur code :monkey:s are trying to figure out what went wrong ...[/blink]')

    with open(LOG_PATH, 'a') as log_file:
        log_file.write(to_print+'\n')
    
    return ok


def admin_dash(cursor, trno):
    cursor.execute("SELECT COUNT(*) FROM students")
    number = cursor.fetchone()