# user.py: user logging, creation, edits, delete

import os, rich, re
from PyInquirer import prompt, Separator
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

def check_trno(trno):
    if len(trno) == 6:
        if trno[0] == "T" and trno[1:6].isdigit():
            return True
    else:
        return False
    

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

def get_existing_teachers(cursor, subject):
    existing_choices = [
        Separator(f"== {subject} Teachers =="),
    ]
    cursor.execute("select TrNO, Name from teachers where Subject='{}';".format(subject))
    output = cursor.fetchall()
    if len(output) != 0:
        for teacher in output:
            existing_choices.append({"name": f"{teacher[1]} (ID: {teacher[0]})"})
    else:
        existing_choices.append({"name": f"No {subject} teacher found in Teacher DB"})
    return existing_choices

def teacher_create_prompt(db, cursor, trno, pswd_hash): 
    trno = trno.upper()
    console = rich.console.Console()
    table = rich.table.Table(
        show_header=True, header_style="bold orange", show_footer=False
    )
    console.print("🆕 [bold green] New Teacher Registration Form [/bold green]\n")
    questions = prompts.get_admin_questions()
    answers = prompt(questions)

    if not answers["is_counselor"]:
        # print(trno, pswd_hash, answers)
        query = "insert into teachers values ('{}', '{}', {}, '{}', '{}');".format(
            trno,
            answers["full_name"].title(),
            answers["is_counselor"],
            answers["subject"],
            pswd_hash,
        )

    else:
        query = "insert into teachers values ('{}', '{}', {}, {}, '{}');".format(
            trno, answers["full_name"].title(), answers["is_counselor"], "NULL", pswd_hash
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
    ok_admin = "not-ok"

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

    is_counselor = True if bool(answers["is_counselor"]) else False

    return ok_admin, is_counselor


def counselor_dash(db, cursor, trno):
    console = rich.console.Console()
    ttable = rich.table.Table(
        show_header=True, show_footer=False, header_style="bold blue"
    )
    ttable.box = rich.box.SIMPLE_HEAD
    cursor.execute("SELECT COUNT(*) FROM students")
    number = cursor.fetchone()[0]
    console.print(
        f"\n[bold green]Students Registered[/bold green]: [magenta]{number}[magenta]\n\n"
    )
    cursor.execute(
        f"SELECT TrNO, Name, Subject, IS_COUNSELOR from teachers where TrNO='{trno}';"
    )
    output = cursor.fetchone()
    ttable.title = "[not italic]📋[/] Your Login Details"
    ttable.add_column("ID")
    ttable.add_column("Teacher Name", width=18)
    ttable.add_column("Subject", justify="center")
    ttable.add_column("Counselor?", justify="center")
    ttable.add_row(
        f"[bold]{trno}[/]",
        f"{output[1].title()}",
        f"{output[2]}" if output[2] != None else "[italic]--NA--[/]",
        "✅" if bool(output[3]) else "❌",
    )
    notif_panel = notifs.panel(cursor, "bruh", admin=True)
    ref_panel = helpers.deadlines_panel()
    console.print(Columns([notif_panel, Panel(ttable), ref_panel]))

    see_crud = True
    while see_crud:
        optionAnswer = prompt(prompts.get_admin_options())

        if optionAnswer["option"] == "Search for a student":
            searchMethodAnswer = prompt(prompts.get_admin_search_method())
            if searchMethodAnswer["method"] == "Search by AdmnNO":
                while True:
                    s_admnno = str(input("Enter the admission number: "))
                    if helpers.check_admnno(s_admnno):
                        break
                    else:
                        console.print("Invalid admission number. [italic]Please try again.[/]")
                cursor.execute(
                    f"SELECT AdmnNO, Name, Class, Stream FROM students WHERE AdmnNO = '{s_admnno}'"
                )
                record = cursor.fetchone()
                if record == None:
                    console.print("[red]No students found.[/]")
                    continue
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

                console.print(table, justify="center")

            elif searchMethodAnswer["method"] == "Search by Class-Section":
                while True:
                    s_clsec = str(input("Enter the Class and section (eg, 12J): ")).upper()
                    if helpers.check_clsec(s_clsec):
                        break
                    else:
                        console.print("Invalid Class and Section. [italic]Please try again.[/]")
                cursor.execute(
                    f"SELECT AdmnNO, Name, Class, Stream FROM students WHERE Class = '{s_clsec}'"
                )
                records = cursor.fetchall()
                if len(records) == 0:
                    console.print("[red]No students found.[/]")
                    continue
                table = rich.table.Table(
                    show_header=True, header_style="bold green", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify="center")

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
                            "ARTS",
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

                if len(records) == 0:
                    console.print("[red]No students found.[/]")
                    continue

                table = rich.table.Table(
                    show_header=True, header_style="bold yellow", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify="center")

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

                dl = s_deadline_answer["deadline"][
                    s_deadline_answer["deadline"].find("(")
                    + 1 : s_deadline_answer["deadline"].find(")")
                ]
                cursor.execute(
                    "SELECT applications.AdmnNO, students.Name, students.Class, students.Stream, applications.CollegeID, colleges.CollegeName, applications.Deadline FROM students JOIN applications ON students.AdmnNO = applications.AdmnNO JOIN colleges ON colleges.CollegeID = applications.CollegeID WHERE applications.Deadline = '{}';".format(
                        dl
                    )
                )
                records = cursor.fetchall()

                if len(records) == 0:
                    console.print("[red]No students found.[/]")
                    continue

                table = rich.table.Table(
                    show_header=True, header_style="bold magenta", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")
                table.add_column("College ID")
                table.add_column("College Name")
                table.add_column("Deadline")

                for record in records:
                    table.add_row(
                        f"{record[0]}",
                        f"{record[1]}",
                        f"{record[2]}",
                        f"{record[3]}",
                        f"{record[4]}",
                        f"{record[5]}",
                        f"{record[6]}",
                    )

                console.print(table, justify="center")
        elif optionAnswer["option"] == "Update status of a student (documents)":
            
            while True:
                change_status_admnno = prompt(
                    [
                        {
                            "type": "input",
                            "name": "admnno",
                            "message": "Enter the Admn. No. of the student you want to change the status of \n  If the Admn. No. is not known, search for the student first \n  (Press Enter to go back)",
                        }
                    ]
                )
                if len(change_status_admnno["admnno"]) == 0:
                    break

                sadmnno = change_status_admnno["admnno"].title()
                if helpers.check_admnno(sadmnno):
                    break
                else:
                    console.print("Invalid admission number. [italic]Please try again.[/]")
            
            if len(change_status_admnno["admnno"]) == 0:
                continue


            cursor.execute(
                f"SELECT * from students WHERE admnno = '{sadmnno}'"
            )
            records = cursor.fetchall()

            if len(records) == 0:
                console.print("[red]Student not found.[/]")
                continue

            cursor.execute(
                f"SELECT AdmnNO, Name, FinalTranscript, CounselorLOR, MidYearReport, PredictedMarks FROM students WHERE AdmnNO = '{sadmnno}'"
            )
            record = cursor.fetchone()

            table2 = rich.table.Table(
                show_header=True, header_style="bold blue", show_footer=False
            )
            table2.add_column("Admn. No")
            table2.add_column("Student Name", width=20)
            table2.add_column("Final Transcript", justify="center")
            table2.add_column("Counselor LOR", justify="center")
            table2.add_column("Mid-Year Report", justify="center")
            table2.add_column("Predicted Marks", justify="center")

            table2.add_row(
                f"{record[0]}",
                f"{record[1]}",
                "❌" if record[2] == 0 else "✅",
                "❌" if record[3] == 0 else "✅",
                "❌" if record[4] == 0 else "✅",
                "❌" if record[5] == 0 else "✅",
            )
            console.print(table2, justify="center")
            
            change_status_college = prompt(
                [
                    {
                        "type": "confirm",
                        "name": "FT_status",
                        "message": "Has the Final Transcript been submitted?",
                        "default": True,
                    },
                    {
                        "type": "confirm",
                        "name": "CL_status",
                        "message": "Has the Counselor LOR been submitted?",
                        "default": True,
                    },
                    {
                        "type": "confirm",
                        "name": "MYR_status",
                        "message": "Has the Mid-Year report been submitted?",
                        "default": True,
                    },
                    {
                        "type": "confirm",
                        "name": "PM_status",
                        "message": "Have the Predicted Marks been submitted?",
                        "default": True,
                    },
                ]
            )
            
            FT_status = int(change_status_college["FT_status"])
            CL_status = int(change_status_college["CL_status"])
            MYR_status = int(change_status_college["MYR_status"])
            PM_status = int(change_status_college["PM_status"])
            cursor.execute(
                f"UPDATE students SET FinalTranscript = {FT_status}, CounselorLOR = {CL_status}, MidYearReport = {MYR_status}, PredictedMarks = {PM_status} WHERE AdmnNO = '{sadmnno}'"
            )
            db.commit()

            cursor.execute(
                f"SELECT AdmnNO, Name, FinalTranscript, CounselorLOR, MidYearReport, PredictedMarks FROM students WHERE AdmnNO = '{sadmnno}'"
            )
            record = cursor.fetchone()

            table = rich.table.Table(
                show_header=True, header_style="bold blue", show_footer=False
            )
            table.add_column("Admn. No")
            table.add_column("Student Name", width=20)
            table.add_column("Final Transcript", justify="center")
            table.add_column("Counselor LOR", justify="center")
            table.add_column("Mid-Year Report", justify="center")
            table.add_column("Predicted Marks", justify="center")

            table.add_row(
                f"{record[0]}",
                f"{record[1]}",
                "❌" if record[2] == 0 else "✅",
                "❌" if record[3] == 0 else "✅",
                "❌" if record[4] == 0 else "✅",
                "❌" if record[5] == 0 else "✅",
            )
            console.print(table, justify="center")
            print()

        elif optionAnswer["option"] == "Add a college to the database":
            col_table = rich.table.Table(
                show_header=True, header_style="bold orange", show_footer=False
            )
            col_table.box = rich.box.SIMPLE_HEAD
            col_table.title = "[not italic]:school:[/] Colleges"
            cursor.execute(
                "SELECT CollegeID, CollegeName FROM colleges ORDER BY CollegeID"
            )
            colleges = cursor.fetchall()

            col_table.add_column("College ID", justify="right")
            col_table.add_column("College Name")

            for college in colleges:
                col_table.add_row(f"{college[0]}", f"{college[1]}")
            console.print(col_table, justify="center")
            add_college = prompt(
                [
                    {
                        "type": "input",
                        "name": "collegeName",
                        "message": "Enter the name of the College to add",
                    },
                    {
                        "type": "confirm",
                        "name": "collegeConfirm",
                        "message": "Are you sure you want to add this college?",
                        "default": True,
                    },
                ]
            )

            if add_college["collegeConfirm"]:
                try:
                    cursor.execute(
                        f"INSERT INTO colleges (CollegeName) values ('{add_college['collegeName']}')"
                    )
                    db.commit()
                    console.print("College added ✅")
                except:
                    console.print("[red]Could not add college.[/]")
            else:
                console.print("[blue]College not added[/]")

        elif optionAnswer["option"] == "Delete a college from the database":
            col_table = rich.table.Table(
                show_header=True, header_style="bold blue", show_footer=False
            )
            col_table.box = rich.box.SIMPLE_HEAD
            col_table.title = "[not italic]:school:[/] Colleges"
            cursor.execute(
                "SELECT CollegeID, CollegeName FROM colleges ORDER BY CollegeID"
            )
            colleges = cursor.fetchall()

            col_table.add_column("College ID", justify="right")
            col_table.add_column("College Name")

            for college in colleges:
                col_table.add_row(f"{college[0]}", f"{college[1]}")
            console.print(col_table, justify="center")
            while True:
                delete_college = prompt(
                    [
                        {
                            "type": "input",
                            "name": "collegeID",
                            "message": "Enter the College ID to delete",
                        },
                        {
                            "type": "confirm",
                            "name": "collegeConfirm",
                            "message": "Are you sure you want to delete this college? \n(This will delete applications of all students to this college) [IRREVERSIBLE]",
                            "default": True,
                        },
                    ]
                )

                try:
                    cID = int(delete_college["collegeID"])
                    for college in colleges:
                        if college[0] == cID:
                            break
                    else:
                        console.print("[bold red]College ID not found.[/]")
                        continue
                    break
                except ValueError:
                    console.print("[red]Invalid College ID.[/]")

            cursor.execute(
                f"SELECT CollegeName FROM colleges WHERE CollegeID = {delete_college['collegeID']}"
            )
            check = cursor.fetchall()
            if delete_college["collegeConfirm"] and not check == None:
                try:
                    cursor.execute(
                        f"DELETE FROM colleges WHERE CollegeID = {delete_college['collegeID']}"
                    )
                    cursor.execute(
                        f"DELETE FROM applications WHERE CollegeID = {delete_college['collegeID']}"
                    )

                    db.commit()
                    console.print("College deleted ✅")
                except:
                    console.print("[red]Could not delete college[/]")
            else:
                console.print("[blue]College not deleted[/]")

        elif optionAnswer["option"] == "Add a session/notification":
            add_session = prompt(
                [
                    {
                        "type": "input",
                        "name": "description",
                        "message": "Description of the Session/Notification (max 255 characters):",
                    },
                    {
                        "type": "input",
                        "name": "date",
                        "message": "Enter the date (or deadline) in YYYY-MM-DD format:",
                        "default": "2020-12-31",
                    },
                    {
                        "type": "list",
                        "name": "audi",
                        "message": "Select a Stream or Group",
                        "choices": [
                            Separator("=== Streams ==="),
                            "PCB",
                            "PCMC",
                            "PCMB",
                            "PCME",
                            "COMM.",
                            "HUMA.",
                            "ARTS",
                            Separator("=== Groups ==="),
                            "Science (Medical)",
                            "Science (Non-Medical)",
                            "Science (All)",
                            "Non-Science",
                            "All Streams",
                        ],
                    },
                    {
                        "type": "confirm",
                        "name": "seshConfirm",
                        "message": "Confirm?",
                        "default": True,
                    },
                ]
            )
            audi = add_session["audi"]
            desc = add_session["description"]
            
            if len(desc) > 255:
                console.print("[red]Description too long, session not added[/]")
                continue

            dat = add_session["date"]
            audiList = [audi]
            if audi == "Science (Medical)":
                audiList = ["PCB", "PCMB"]
            elif audi == "Science (Non-Medical)":
                audiList = ["PCMB", "PCMC", "PCME"]
            elif audi == "Science (All)":
                audiList = ["PCB", "PCMB", "PCMC", "PCME"]
            elif audi == "Non-Science":
                audiList = ["COMM.", "HUMA.", "ARTS"]
            elif audi == "All Streams":
                audiList = ["PCB", "PCMC", "PCMB", "PCME", "COMM.", "HUMA.", "ARTS"]

            cursor.execute("SELECT COALESCE(MAX(GroupID) + 1, 1) FROM notifications")
            grpID = str(cursor.fetchone()[0])

            if add_session["seshConfirm"]:
                for s in audiList:
                    cursor.execute(
                        f"INSERT INTO notifications (Audience, Date, Description, GroupID) VALUES ('{s}', '{dat}', '{desc}', {grpID})"
                    )
                db.commit()
                console.print("[bold green]Session added.[/]")

                stable = rich.table.Table(
                show_header=True, header_style="bold green", show_footer=False
                )
                stable.box = rich.box.MINIMAL
                stable.title = "[not italic]🔔[/] Notifications"
                stable.add_column("Notif. ID")
                stable.add_column("Date")
                stable.add_column("Description")
                stable.add_column("Stream")
                cursor.execute(
                    "SELECT GroupID, Date, Description, Audience FROM notifications"
                )
                records = cursor.fetchall()
                for record in records:
                    stable.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(stable, justify="center")
            else:
                console.print("[blue]Session not added[/]")

        elif optionAnswer["option"] == "Cancel a session/notification":
            stable = rich.table.Table(
                show_header=True, header_style="bold yellow", show_footer=False
            )
            stable.box = rich.box.MINIMAL
            stable.title = "[not italic]🔔[/] Notifications"
            stable.add_column("Notif. ID")
            stable.add_column("Date")
            stable.add_column("Description")
            stable.add_column("Stream")
            cursor.execute(
                "SELECT GroupID, Date, Description, Audience FROM notifications"
            )
            records = cursor.fetchall()
            for record in records:
                stable.add_row(
                    f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                )

            console.print(stable, justify="center")

            while True:
                cancel_session = prompt(
                    [
                        {
                            "type": "input",
                            "name": "notifID",
                            "message": "Enter the ID of the notification you would like to cancel/delete:",
                        },
                        {
                            "type": "confirm",
                            "name": "notifConfirm",
                            "message": "Confirm?",
                            "default": True,
                        },
                    ]
                )
                try:
                    notifID = int(cancel_session["notifID"])
                    for record in records:
                        if record[0] == notifID:
                            break
                    else:
                        console.print("[red]Notification ID not found.[/]")
                        continue
                    break
                except ValueError:
                    console.print("[bold red]Invalid Notification ID.[/]")

            if cancel_session["notifConfirm"]:
                cursor.execute(
                    f"DELETE FROM notifications WHERE GroupID = '{cancel_session['notifID']}'"
                )
                db.commit()
                console.print("[bold green]Session deleted.[/]")
            else:
                console.print("[blue]Session not deleted.[/]")

        elif optionAnswer["option"] == "Exit IntlApp Dashboard":
            console.print("\n\n[dim]Exiting the application...[/]")
            see_crud = False
            break

        elif optionAnswer["option"] == "Delete your IntlApp account and exit":
            delete_confirm = prompt(
                [
                    {
                        "type": "confirm",
                        "name": "delete",
                        "message": "Are you sure you want to delete your account? [IRREVERSIBLE]",
                        "default": False,
                    }
                ]
            )
            if delete_confirm["delete"]:
                cursor.execute("delete from teachers where TrNO='{}';".format(trno))
                db.commit()
                console.print(
                    "\n😔 We're sorry to see you go.\n\n[italic red]Your account was deleted.[/]",
                    justify="center",
                )
                see_crud = False
                console.print("\n\n[dim]Exiting the appplication...[/]")
            break

        elif optionAnswer["option"] == "Hide this prompt":
            console.print(":eyes: The prompt is hidden.\n")
            show = str(input("Press enter to show it again:"))
            if len(show) == 0:
                see_crud = True

        else:
            break


def teacher_dash(db, cursor, trno):
    console = rich.console.Console()
    ltable =  rich.table.Table(
        show_header=True, show_footer=False, header_style="bold blue"
    )
    ttable = rich.table.Table(
        show_header=True, show_footer=False, header_style="bold magenta"
    )
    ttable.box = rich.box.SIMPLE_HEAD
    ltable.box = rich.box.SIMPLE_HEAD
    cursor.execute("SELECT COUNT(*) FROM students")
    number = cursor.fetchone()[0]
    console.print(
        f"\n[bold green]Students Registered[/bold green]: [magenta]{number}[magenta]\n\n"
    )
    cursor.execute(
        f"SELECT TrNO, Name, Subject, IS_COUNSELOR from teachers where TrNO='{trno}';"
    )
    output = cursor.fetchone()
    ttable.title = "[not italic]📋[/] Your Login Details"
    ttable.add_column("ID")
    ttable.add_column("Teacher Name", width=18)
    ttable.add_column("Subject", justify="center")
    ttable.add_column("Counselor?", justify="center")
    ttable.add_row(
        f"[bold]{trno}[/]",
        f"{output[1].title()}",
        f"{output[2]}" if output[2] != None else "[italic]--NA--[/]",
        "✅" if bool(output[3]) else "❌",
    )

    cursor.execute(f"SELECT students.AdmnNO, students.Name, students.Class, lors.Submitted FROM students JOIN lors ON students.AdmnNO = lors.AdmnNO WHERE lors.TrNO = '{trno}'")
    outputs = cursor.fetchall()
    ltable.title = "[not italic]📋[/] Status of LORs"
    ltable.add_column("Admn. No.")
    ltable.add_column("Student Name", width=18)
    ltable.add_column("Class", justify="center")
    ltable.add_column("Submitted?", justify="center")
    for output in outputs:
        ltable.add_row(
            f"[bold]{output[0]}[/]",
            f"{output[1].title()}",
            f"{output[2]}",
            "✅" if bool(output[3]) else "❌",
        )
    console.print(Columns([Panel(ttable), Panel(ltable)]), justify="center")

    see_crud = True
    while see_crud:
        optionAnswer = prompt(prompts.get_teacher_options())

        if optionAnswer["option"] == "Search for a student":
            searchMethodAnswer = prompt(prompts.get_admin_search_method())
            if searchMethodAnswer["method"] == "Search by AdmnNO":
                while True:
                    s_admnno = str(input("Enter the admission number: "))
                    if helpers.check_admnno(s_admnno):
                        break
                    else:
                        console.print("Invalid admission number. [italic]Please try again.[/]")
                cursor.execute(
                    f"SELECT AdmnNO, Name, Class, Stream FROM students WHERE AdmnNO = '{s_admnno}'"
                )
                record = cursor.fetchone()
                if record == None:
                    console.print("[red]No students found.[/]")
                    continue
                table = rich.table.Table(
                    show_header=True, header_style="bold orange", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=18)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                table.add_row(
                    f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                )

                console.print(table, justify="center")

            elif searchMethodAnswer["method"] == "Search by Class-Section":
                while True:
                    s_clsec = str(input("Enter the Class and section (eg, 12J): ")).upper()
                    if helpers.check_clsec(s_clsec):
                        break
                    else:
                        console.print("Invalid Class and Section. [italic]Please try again.[/]")
                cursor.execute(
                    f"SELECT AdmnNO, Name, Class, Stream FROM students WHERE Class = '{s_clsec}'"
                )
                records = cursor.fetchall()
                if len(records) == 0:
                    console.print("[red]No students found.[/]")
                    continue
                table = rich.table.Table(
                    show_header=True, header_style="bold cyan", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify="center")

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
                            "ARTS",
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

                if len(records) == 0:
                    console.print("[red]No students found.[/]")
                    continue

                table = rich.table.Table(
                    show_header=True, header_style="bold ", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")

                for record in records:
                    table.add_row(
                        f"{record[0]}", f"{record[1]}", f"{record[2]}", f"{record[3]}"
                    )

                console.print(table, justify="center")

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

                dl = s_deadline_answer["deadline"][
                    s_deadline_answer["deadline"].find("(")
                    + 1 : s_deadline_answer["deadline"].find(")")
                ]
                cursor.execute(
                    "SELECT applications.AdmnNO, students.Name, students.Class, students.Stream, applications.CollegeID, colleges.CollegeName, applications.Deadline FROM students JOIN applications ON students.AdmnNO = applications.AdmnNO JOIN colleges ON colleges.CollegeID = applications.CollegeID WHERE applications.Deadline = '{}';".format(
                        dl
                    )
                )
                records = cursor.fetchall()

                if len(records) == 0:
                    console.print("[red]No students found.[/]")
                    continue

                table = rich.table.Table(
                    show_header=True, header_style="bold magenta", show_footer=False
                )
                table.add_column("Admn. No")
                table.add_column("Student Name", width=20)
                table.add_column("ClassSection", justify="left")
                table.add_column("Stream")
                table.add_column("College ID")
                table.add_column("College Name")
                table.add_column("Deadline")

                for record in records:
                    table.add_row(
                        f"{record[0]}",
                        f"{record[1]}",
                        f"{record[2]}",
                        f"{record[3]}",
                        f"{record[4]}",
                        f"{record[5]}",
                        f"{record[6]}",
                    )

                console.print(table, justify="center")
        
        # Add this option in a later commit
        elif optionAnswer["option"] == "Update status of a Student LOR":
            
            change_lor_status = prompt(
                [
                    {
                        "type": "list",
                        "name": "sname",
                        "message": "Select the student whose LOR status you'd like to change: ",
                        "choices": [
                            f"{record[1]} ({record[0]})" for  record in outputs
                        ]
                    },
                    {
                        "type": "confirm",
                        "name": "isSubmitted",
                        "message": "Has the LOR been submitted?",
                        "default": True
                    },
                    {
                        "type": "confirm",
                        "name": "confirmed",
                        "message": "Confirm?",
                        "default": True
                    }
                ]
            )
            if change_lor_status["confirmed"]:
                if change_lor_status["isSubmitted"]:
                    admnno = re.findall('[R|E|V][0-9][0-9][0-9][0-9][0-9]', change_lor_status['sname'])[0]
                    cursor.execute(f"UPDATE lors SET submitted = 1 where admnno = '{admnno}' AND TrNO = '{trno}'")
                    db.commit()
                else:
                    admnno = re.findall('[R|E|V][0-9][0-9][0-9][0-9][0-9]', change_lor_status['sname'])[0]
                    cursor.execute(f"UPDATE lors SET submitted = 0 where admnno = '{admnno}' AND TrNO = '{trno}'")
                    db.commit()
                console.print("[green]Status updated.[/]")
            else:
                console.print("[blue]Status not updated.[/]")

            cursor.execute(f"SELECT students.AdmnNO, students.Name, students.Class, lors.Submitted FROM students JOIN lors ON students.AdmnNO = lors.AdmnNO WHERE lors.TrNO = '{trno}'")
            outputs2 = cursor.fetchall()
            
            lortable = rich.table.Table(show_header=True, show_footer=False, header_style="bold blue")
            lortable.box = rich.box.SIMPLE_HEAD
            lortable.title = "[not italic]📋[/] Status of LORs"
            lortable.add_column("Admn. No.")
            lortable.add_column("Student Name", width=18)
            lortable.add_column("Class", justify="center")
            lortable.add_column("Submitted?", justify="center")
            for output in outputs2:
                lortable.add_row(
                    f"[bold]{output[0]}[/]",
                    f"{output[1].title()}",
                    f"{output[2]}",
                    "✅" if bool(output[3]) else "❌",
                )
            console.print(Columns([lortable,]), justify="center")

        
        elif optionAnswer["option"] == "Exit IntlApp Dashboard":
            console.print("\n\n[dim]Exiting the application...[/]")
            see_crud = False
            break

        elif optionAnswer["option"] == "Delete your IntlApp account and exit":
            delete_confirm = prompt(
                [
                    {
                        "type": "confirm",
                        "name": "delete",
                        "message": "Are you sure you want to delete your account? [IRREVERSIBLE]",
                        "default": False,
                    }
                ]
            )
            if delete_confirm["delete"]:
                cursor.execute("delete from teachers where TrNO='{}';".format(trno))
                db.commit()
                console.print(
                    "\n😔 We're sorry to see you go.\n\n[italic red]Your account was deleted.[/]",
                    justify="center",
                )
                see_crud = False
                console.print("\n\n[dim]Exiting the appplication...[/]")
            break

        elif optionAnswer["option"] == "Hide this prompt":
            console.print(":eyes: The prompt is hidden.\n")
            show = str(input("Press enter to show it again:"))
            if len(show) == 0:
                see_crud = True

        else:
            break
