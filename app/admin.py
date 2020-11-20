# user.py: user logging, creation, edits, delete

import os, rich
from PyInquirer import prompt
import mysql.connector as mysql
import prompts, notifs, helpers
from rich.columns import Columns
from rich.panel import Panel

def teacher_create_table(cursor):
    console = rich.console.Console()
    query = "CREATE TABLE IF NOT EXISTS teachers (TrNO CHAR(6) NOT NULL, Name VARCHAR(255) NOT NULL, IS_COUNSELOR BOOLEAN NOT NULL, Subject VARCHAR(15), PSWDHASH CHAR(60) NOT NULL, PRIMARY KEY (TrNO));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "bruh"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE TEACHER"
    except Exception:
        console.print(":bulb: Existing teacher table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def exists(cursor, trno):
    global exists
    exists = False
    cursor.execute("select IS_COUNSELOR from teachers where TrNO='{}';".format(trno))
    output = cursor.fetchone()
    # print(output)
    is_counselor = False
    if output != None:
        exists = True
        is_counselor = bool(output[0])
    return exists, is_counselor


def get_pswdhash(cursor, trno):
    trno = trno.upper()
    cursor.execute("select PSWDHASH from teachers where TrNO='{}';".format(trno))
    output = cursor.fetchone()
    return output[0].encode("ascii")


def teacher_create_prompt(db, cursor, trno, pswd_hash):
    trno = trno.upper()
    console = rich.console.Console()
    table = rich.table.Table(
        show_header=True, header_style="bold magenta", show_footer=False
    )
    console.print("🆕 [bold green] New Teacher Registration Form [/bold green]\n")
    questions = prompts.get_admin_questions()
    answers = prompt(questions)

    if not answers["is_counselor"]:
        # print(trno, pswd_hash, answers)
        query = "insert into teachers values ('{}', '{}', {}, '{}', '{}');".format(
            trno,
            answers["full_name"],
            answers["is_counselor"],
            answers["subject"],
            pswd_hash,
        )

    else:
        query = "insert into teachers values ('{}', '{}', {}, {}, '{}');".format(
            trno, answers["full_name"], answers["is_counselor"], "NULL", pswd_hash
        )

    table.add_column("Tr. No.")
    table.add_column("Teacher Name", width=18)
    table.add_column("Counselor?", justify="center")
    table.add_column("Subject", justify="center")
    table.add_column("Additional Info.", justify="left")

    if not answers["is_counselor"]:
        table.add_row(
            f"[bold]{trno}[/]",
            f'{answers["full_name"]}',
            f'{answers["is_counselor"]}',
            f'{answers["subject"]}',
            "Your password is hashed securely with bcrypt.",
        )
    else:
        table.add_row(
            f"[bold]{trno}[/]",
            f'{answers["full_name"]}',
            f'{answers["is_counselor"]}',
            "None",
            "Your password is hashed securely with bcrypt.",
        )

    console.print("\n\n[bold]Your Admin Dashboard[/]\n", justify="center")
    console.print(table, justify="center")
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
    global ok_admin
    ok_admin = 'not-ok'

    if confirmation["verify"] and confirmation["finish"]:
        try:
            cursor.execute(query)
            to_print = "[INSERT] NEW ROW TEACHER"
            db.commit()
            ok_admin = "ok"
        except mysql.Error as e:
            console.print("⚠️ Something Went Wrong :-(")
            to_print = f"[DB ERROR]: INSERTING\nMessage: {e}"
    else:
        console.print(
            "[blink][i]Oopsie wOOpsiee...[/i]\n\nOur code :monkey:s are trying to figure out what went wrong ...[/blink]"
        )

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")

    is_c = "ok" if bool(answers['is_counselor']) else 'not-ok'

    return ok_admin, is_c


def counselor_dash(cursor, trno):
    console = rich.console.Console()
    ttable = rich.table.Table(show_header=True, show_footer=False, header_style="bold magenta")
    ttable.box = rich.box.SIMPLE_HEAD
    cursor.execute("SELECT COUNT(*) FROM students")
    number = cursor.fetchone()[0]
    console.print(
        f"\n[bold green]Students Registered[/bold green]: [magenta]{number}[magenta]\n\n"
    )
    cursor.execute(f"SELECT TrNO, Name, Subject, IS_COUNSELOR from teachers where TrNO='{trno}';")
    output = cursor.fetchone()
    ttable.title = "[not italic]📋[/] Your Login Details"
    ttable.add_column("ID")
    ttable.add_column("Teacher Name", width=18)
    ttable.add_column("Subject", justify="center")
    ttable.add_column("Counselor?", justify="center")
    ttable.add_row(
        f"[bold]{trno}[/]",
        f"{output[1].title()}",
        f"{output[2]}" if output[2] != None else '[italic]--NA--[/]',
        "✅" if bool(output[3]) else '❌',
    )
    notif_panel = notifs.panel(cursor, 'bruh', admin=True)
    ref_panel = helpers.deadlines_panel()
    console.print(
        Columns([notif_panel, Panel(ttable), ref_panel])
    )

    while True:
        optionAnswer = prompt(prompts.get_admin_options())

        if optionAnswer["option"] == "Search for a student":
            searchMethodAnswer = prompt(prompts.get_admin_search_method())
            if searchMethodAnswer["method"] == "Search by AdmnNO":
                s_admnno = str(input("Enter the admission number: "))
                cursor.execute(
                    f"SELECT AdmnNO, Name, Class, Stream FROM students WHERE AdmnNO = '{s_admnno}'"
                )
                record = cursor.fetchone()
                table = rich.table.Table(
                    show_header=True, header_style="bold magenta", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=18)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                table.add_row(
                    f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                )

                console.print(table, justify='center')

            elif searchMethodAnswer["method"] == "Search by Class-Section":
                s_clsec = str(input("Enter the Class and section (eg, 12J): "))
                cursor.execute(
                    f"SELECT AdmnNO, Name, Class, Stream FROM students WHERE Class = '{s_clsec}'"
                )
                records = cursor.fetchall()
                table = rich.table.Table(
                    show_header=True, header_style="bold magenta", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify='center')

            elif searchMethodAnswer["method"] == "Search by Stream":
                s_stream_prompt = [
                    {
                        "type": "list",
                        "name": "stream",
                        "message": "Select Stream",
                        "choices": [
                            "PCB",
                            "PCMC",
                            "PCMB",
                            "PCME",
                            "COMM.",
                            "HUMA.",
                            "OTHER",
                        ],
                    },
                ]
                s_stream_answer = prompt(s_stream_prompt)

                cursor.execute(
                    "SELECT AdmnNO, Name, Class, Stream FROM students WHERE Stream = '{}';".format(
                        s_stream_answer["stream"]
                    )
                )
                records = cursor.fetchall()
                table = rich.table.Table(
                    show_header=True, header_style="bold magenta", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify='center')

            elif searchMethodAnswer["method"] == "Search by Deadline":
                s_deadline_prompt = [
                    {
                        "type": "list",
                        "name": "deadline",
                        "message": "Select Deadline",
                        "choices": [
                            "November first-week (US_EARLY1)",
                            "Mid-November (UK/US_EARLY2)",
                            "November End (US_UCs)",
                            "January first-week (UK/US_REGULAR)",
                            "Not decided (ND)",
                        ],
                    }
                ]
                s_deadline_answer = prompt(s_deadline_prompt)

                cursor.execute(
                    "SELECT AdmnNO, Name, Class, Stream FROM students WHERE Stream = '{}';".format(
                        s_stream_answer["stream"]
                    )
                )
                records = cursor.fetchall()
                table = rich.table.Table(
                    show_header=True, header_style="bold magenta", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify='center')
        # elif optionAnswer["option"] == "Update status of a student":
        #     print("todo")
        elif optionAnswer["option"] == "Add a college to the database":
            print("todo")
