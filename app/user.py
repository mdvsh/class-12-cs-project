# user.py: user logging, creation, edits, delete

import os, rich
from PyInquirer import prompt
import mysql.connector as mysql

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

def exists(cursor, admnno):
    global exists
    exists = False
    cursor.execute("select * from students where AdmnNO='{}';".format(admnno))
    output = cursor.fetchone()
    # print(output)
    if output != None:
        exists = True
    return exists

def get_pswdhash(cursor, admnno):
    admnno = admnno.upper()
    cursor.execute("select PSWDHASH from students where AdmnNO='{}';".format(admnno))
    output = cursor.fetchone()
    return output[0].encode('ascii')

def student_create_prompt(db, cursor, admnno, pswd_hash):
    admnno = admnno.upper()
    console = rich.console.Console()
    table = rich.table.Table(show_header=True, header_style="bold magenta", show_footer=False)
    console.print('🆕 [bold green] New Student Registration Form [/bold green]\n')
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

    # print(admnno, pswd_hash, answers)
    query = "insert into students values ('{}', '{}', '{}', '{}', '{}');".format(admnno, answers['full_name'], answers['clsec'], answers['stream'], pswd_hash)

    table.add_column("Admn. No.")
    table.add_column("Student Name", width=18)
    table.add_column("Class/Section", justify='center')
    table.add_column("Stream", justify='center')
    table.add_column("Additional Info.", justify='left')
    table.add_row(
        f'[bold]{admnno}[/]',
        f'{answers["full_name"]}',
        f'{answers["clsec"]}',
        f'{answers["stream"]}',
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
            to_print = '[INSERT] NEW ROW STUDENT'
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