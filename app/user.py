# user.py: user logging, creation, edits, delete

import os
import rich
from PyInquirer import prompt, Separator
import mysql.connector as mysql
import prompts


def student_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists students(AdmnNO char(6) NOT NULL, Name varchar(255) NOT NULL, Class char(3) NOT NULL, Stream varchar(5) NOT NULL, PSWDHASH CHAR(60) NOT NULL, PRIMARY KEY (AdmnNO));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE STUDENT TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE STUDENT"
    except Exception:
        console.print(":bulb: Existing student table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def college_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists colleges(CollegeID int not null auto_increment, CollegeName varchar(255) not null unique, primary key (CollegeID));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE COLLEGE TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE COLLEGE"
    except Exception:
        console.print(":bulb: Existing college table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def add_college(db, cursor, name):
    console = rich.console.Console()
    query = "insert into colleges(Name) values('{}');".format(name)
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE COLLEGE TABLE"
    try:
        cursor.execute(query)
        to_print = "[INSERT] NEW ROW COLLEGE"
        db.commit()
    # add handling if college already exists
    except mysql.Error as e:
        console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: INSERTING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def get_existing_colleges(cursor):
    existing_choices = [
        Separator("== Colleges (Already in Database) =="),
    ]
    cursor.execute("select Name from colleges;")
    output = cursor.fetchall()
    for college_t in output:
        existing_choices.append({"name": college_t[0]})
    return existing_choices


# archived (not recommended for use in production)


def exists(cursor, admmno):
    global exists
    exists = False
    cursor.execute("select * from students where AdmnNO='{}';".format(admmno))
    output = cursor.fetchone()
    # print(output)
    if output != None:
        exists = True
    return exists


def get_pswdhash(cursor, admnno):
    admnno = admnno.upper()
    cursor.execute("select PSWDHASH from students where AdmnNO='{}';".format(admnno))
    output = cursor.fetchone()
    return output[0].encode("ascii")


def login_display_student(db, cursor, admnno):
    admnno = admnno.upper()
    console = rich.console.Console()
    table = rich.table.Table(
        show_header=True, header_style="bold magenta", show_footer=False
    )

    cursor.execute("select * from students where AdmnNO='{}';".format(admnno))
    output = cursor.fetchone()
    table.add_column("Admn. No.")
    table.add_column("Student Name", width=18)
    table.add_column("Class/Section", justify="center")
    table.add_column("Stream", justify="center")
    table.add_column("Additional Info.", justify="left")
    table.add_row(
        f"[bold]{admnno}[/]",
        f"{output[1].title()}",
        f"{output[2]}",
        f"{output[3]}",
        "Your password is securely hashed for verification.",
    )

    console.print("\n\n[yellow]Here's what we got from you[/]\n", table)


def student_create_prompt(db, cursor, admnno, pswd_hash):
    admnno = admnno.upper()
    console = rich.console.Console()
    table = rich.table.Table(
        show_header=True, header_style="bold magenta", show_footer=False
    )
    console.print("🆕 [bold green] New Student Registration Form [/bold green]\n")

    existing_choices = get_existing_colleges(cursor)

    college_prompt = {
        "type": "checkbox",
        "qmark": "🎓",
        "message": "Select or Add Colleges to your Watchlist",
        "name": "colleges",
        "choices": existing_choices,
    }

    questions = prompts.get_student_questions()
    answers = prompt(questions)
    if answers["stream"] == "OTHER":
        other_stream = str(input("Enter other stream (5 letters): "))
        answers["stream"] = other_stream
    # college prompt

    college_questions = prompts.get_college_questions()
    college_questions.insert(0, college_prompt)
    canswers = prompt(college_questions)
    college_list = []
    college_toadd_list = []
    for c in canswers["colleges"]:
        if c != "Add it below!":
            cd = {}
            cd["ND"] = c
            college_list.append(cd)
    try:
        s = canswers["deadline"]
        cd = {}
        cd[s[s.find("(") + 1 : s.find(")")]] = canswers["new_college"].title()
        college_list.append(cd)
        college_toadd_list.append(cd)
    except KeyError:
        pass

    watchlist = ""
    for coll in college_list:
        for k, v in coll.items():
            watchlist += "[bold green]{}[/] : {}\n".format(k, v)

    new_user_query = (
        "insert into students values ('{}', '{}', '{}', '{}', '{}');".format(
            admnno,
            answers["full_name"].title(),
            answers["clsec"],
            answers["stream"],
            pswd_hash,
        )
    )

    table.add_column("Admn. No.")
    table.add_column("Student Name", width=18)
    table.add_column("Class/Section", justify="center")
    table.add_column("Stream", justify="center")
    table.add_column("Watchlist (Deadline / Name)", justify="left")
    table.add_row(
        f"[bold]{admnno}[/]",
        f'{answers["full_name"].title()}',
        f'{answers["clsec"]}',
        f'{answers["stream"]}',
        f"{watchlist}",
    )

    console.print("\n\n[yellow]Here's what we got from you[/]\n", table)

    # inquirer to confrim user details before adding
    confirm = [
        {
            "type": "confirm",
            "message": "Are all the details correct?",
            "name": "verify",
            "default": True,
        },
        {
            "type": "confirm",
            "message": "Finish registration?",
            "name": "finish",
            "default": True,
        },
    ]

    confirmation = prompt(confirm)

    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT INSERT ROW"
    global ok_student
    ok_student = "not-ok"

    for c in college_toadd_list:
        name = list(c.values())[0]
        add_college(db, cursor, name)

    if confirmation["verify"] and confirmation["finish"]:
        try:
            cursor.execute(new_user_query)
            to_print = "[INSERT] NEW ROW STUDENT"
            db.commit()
            ok_student = "ok"
        except mysql.Error as e:
            console.print("⚠️ Something Went Wrong :-(")
            to_print = f"[DB ERROR]: INSERTING\nMessage: {e}"
    else:
        console.print(
            "[blink][i]Oopsie wOOpsiee...[/i]\n\nOur code :monkey:s are trying to figure out what went wrong ...[/blink]"
        )

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")

    return ok_student
