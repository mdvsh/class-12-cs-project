# user.py: user logging, creation, edits, delete

import os, re
import rich
from PyInquirer import prompt, Separator
import mysql.connector as mysql
from rich.columns import Columns
from rich.panel import Panel
import prompts, notifs, admin, lors
import helpers


def student_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists students(AdmnNO char(6) NOT NULL, Name varchar(255) NOT NULL, Class char(3) NOT NULL, Stream varchar(5) NOT NULL, FinalTranscript bool default False not null, CounselorLOR bool default False not null, MidYearReport bool default False not null, PredictedMarks bool default False not null, PSWDHASH CHAR(60) NOT NULL, PRIMARY KEY (AdmnNO));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE STUDENTS TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE STUDENTS"
    except Exception:
        console.print(":bulb: Existing students table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def college_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists colleges(CollegeID int not null auto_increment, CollegeName varchar(255) not null unique, primary key (CollegeID));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE COLLEGES TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE COLLEGES"
    except Exception:
        console.print(":bulb: Existing colleges table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def apps_create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists applications(AdmnNO char(6) not null, CollegeID int not null, Deadline varchar(255) not null, Submitted bool default False not null);"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE APPLICATIONS TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE APPLICATIONS"
    except Exception:
        console.print(":bulb: Existing applications table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def add_college(db, cursor, name):
    console = rich.console.Console()
    query = "insert into colleges(CollegeName) values('{}');".format(name)
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT ADD TO COLLEGE TABLE"
    try:
        cursor.execute(query)
        to_print = "[INSERT] NEW ROW COLLEGE"
        db.commit()
    # add handling if college already exists (done)
    except mysql.Error as e:
        if e.errno == 1062:
            console.print(
                "⚡ [italic]College already exists in database.[/] [magenta]Linking to your new application[/]..."
            )
        else:
            console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: INSERTING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def create_application(db, cursor, studID, collegeID, deadline):
    console = rich.console.Console()
    query = "insert into applications(AdmnNo, CollegeID, Deadline) values('{}', {}, '{}');".format(
        studID, collegeID, deadline
    )
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT ADD TO APPLICATION TABLE"
    try:
        cursor.execute(query)
        to_print = "[INSERT] NEW ROW APPLICATION"
        db.commit()
    # add handling if college already exists
    except mysql.Error as e:
        console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: INSERTING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def delete_application(db, cursor, studID, collegeID):
    console = rich.console.Console()
    query = "delete from applications where AdmnNO='{}' and CollegeID={};".format(
        studID, collegeID
    )
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT DELETE FROM APPLICATION TABLE"
    try:
        cursor.execute(query)
        to_print = "[DELETE] DROP ROW APPLICATION"
        db.commit()
    # add handling if college already exists
    except mysql.Error as e:
        console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: DELETING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def delete_applications(db, cursor, studID):
    console = rich.console.Console()
    query = "delete from applications where AdmnNO='{}';".format(studID)
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT DELETE FROM APPLICATION TABLE"
    try:
        cursor.execute(query)
        to_print = "[DELETE] DROP ROWS APPLICATION"
        db.commit()
    except mysql.Error as e:
        console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: DELETING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")

def delete_lors(db, cursor, studID):
    console = rich.console.Console()
    query = "delete from lors where AdmnNO='{}';".format(studID)
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT DELETE FROM LORS TABLE"
    try:
        cursor.execute(query)
        to_print = "[DELETE] DROP ROWS LORS"
        db.commit()
    except mysql.Error as e:
        console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: DELETING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")

def modify_application(
    db, cursor, studID, collegeID, deadline, sstatus, change_status=False
):
    console = rich.console.Console()
    if change_status:
        query = "update applications set Deadline='{}', Submitted={} where CollegeID={} and AdmnNO='{}';".format(
            deadline, sstatus, collegeID, studID
        )
    else:
        query = "update applications set Deadline='{}' where CollegeID={} and AdmnNO='{}';".format(
            deadline, collegeID, studID
        )
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT MODIFY ROW FROM APPLICATION TABLE"
    try:
        cursor.execute(query)
        to_print = "[UPDATE] MODIFY ROW APPLICATION"
        db.commit()
    # add handling if college already exists
    except mysql.Error as e:
        console.print("⚠️ Something Went Wrong :-(")
        to_print = f"[DB ERROR]: DELETING\nMessage: {e}"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


def get_existing_colleges(cursor):
    existing_choices = [
        Separator("== Colleges (Already in Database) =="),
    ]
    cursor.execute("select CollegeName from colleges;")
    output = cursor.fetchall()
    for college_t in output:
        existing_choices.append({"name": college_t[0]})
    return existing_choices

def get_new_colleges_add(cursor, admnno):
    existing_choices = [
        Separator("== New Colleges from DB (Not Applied To Yet) =="),
    ]
    cursor.execute("select CollegeName from colleges where CollegeID not in (select CollegeID from applications where AdmnNO='{}');".format(admnno))
    output = cursor.fetchall()
    for college_t in output:
        existing_choices.append({"name": college_t[0]})
    return existing_choices

def get_college_id(cursor, cname):
    cursor.execute("select CollegeID from colleges where Name='{}';".format(cname))
    output = cursor.fetchone()
    return output[0]


def get_pswdhash(cursor, admnno):
    admnno = admnno.upper()
    cursor.execute("select PSWDHASH from students where AdmnNO='{}';".format(admnno))
    output = cursor.fetchone()
    return output[0].encode("ascii")


def display_student_tables(db, cursor, admnno):
    admnno = admnno.upper()
    console = rich.console.Console()
    table = rich.table.Table(
        show_header=True, header_style="bold magenta", show_footer=False
    )
    table_two = rich.table.Table(
        show_header=True, header_style="bold yellow", show_footer=False
    )
    table_three = rich.table.Table(
        show_header=True, header_style="bold blue", show_footer=False
    )
    table_four = rich.table.Table(
        show_header=True, header_style="bold red", show_footer=False
    )
    table.box = rich.box.MINIMAL
    table_two.box = rich.box.MINIMAL
    table_three.box = rich.box.MINIMAL
    table_four.box = rich.box.MINIMAL
    cursor.execute("select * from students where AdmnNO='{}';".format(admnno))
    output = cursor.fetchone()
    cursor.execute(
        "SELECT colleges.CollegeID, colleges.CollegeName, applications.deadline, applications.submitted FROM applications JOIN colleges ON colleges.CollegeID = applications.CollegeID WHERE applications.AdmnNO = '{}';".format(
            admnno
        )
    )
    watchlist = cursor.fetchall()

    cursor.execute(f"SELECT teachers.TrNO, teachers.Name, teachers.Subject, lors.Submitted FROM teachers JOIN lors ON teachers.TrNO = lors.TrNO WHERE lors.AdmnNO = '{admnno}'")
    outputs = cursor.fetchall()


    table.title = "[not italic]👤[/] Your Info"
    table.add_column("Admn. No.")
    table.add_column("Student Name", width=18)
    table.add_column("Class/Section", justify="center")
    table.add_column("Stream", justify="center")
    table.add_row(
        f"[bold]{admnno}[/]",
        f"{output[1].title()}",
        f"{output[2]}",
        f"{output[3]}",
    )

    table_two.title = "[not italic]📋[/] Counselor Documents"
    table_two.add_column("Document Name")
    table_two.add_column("Status", justify="center")
    table_two.add_row("[bold]Final Transcript[/]", "✅" if output[4] == 1 else "❌")
    table_two.add_row("[bold]Counselor LOR[/]", "✅" if output[4] == 1 else "❌")
    table_two.add_row("[bold]Mid-Year Report[/]", "✅" if output[4] == 1 else "❌")
    table_two.add_row("[bold]Predicted Marks[/]", "✅" if output[4] == 1 else "❌")

    table_three.title = "[not italic]👀[/] Your Watchlist"
    table_three.add_column("CollegeID", justify="left")
    table_three.add_column("College Name", width=30)
    table_three.add_column("Deadline")
    table_three.add_column("Submitted?", justify="center")
    for college in watchlist:
        table_three.add_row(
            f"[dim]{college[0]}[/]",
            f"{college[1]}",
            f"[bold green]{college[2]}[/]",
            "✅" if college[3] == 1 else "❌",
        )

    table_four.title = "[not italic]📋[/] Status of LORs"
    table_four.add_column("TeacherID")
    table_four.add_column("Teacher Name", width=18)
    table_four.add_column("Subject", justify="center")
    table_four.add_column("Submitted?", justify="center")
    for b in outputs:
        table_four.add_row(
            f"[bold]{b[0]}[/]",
            f"{b[1].title()}",
            f"{b[2]}" if b[2] != None else "[italic]--NA--[/]",
            "✅" if bool(b[3]) else "❌",
        )
    console.print("\n\n[bold]Your Student Dashboard[/]\n", justify="center")
    ref_panel = helpers.deadlines_panel()
    notif_panel = notifs.panel(cursor, output[3])
    console.print(Columns([Panel(table), Panel(table_four), Panel(table_two)]), justify="center")
    console.print(Columns([notif_panel, Panel(table_three), ref_panel], equal=False, expand=False))


def student_dashboard(db, cursor, admnno):
    # crud ops
    admnno = admnno.upper()
    console = rich.console.Console()
    display_student_tables(db, cursor, admnno)
    global see_crud
    see_crud = True
    while see_crud:
        crud_ops = prompt(prompts.get_student_options())
        if crud_ops["opr"] == "Add a college":
            global add
            add, college_list = True, []
            while add:
                existing_choices = get_new_colleges_add(cursor, admnno)
                college_prompt = {
                    "type": "checkbox",
                    "qmark": "🎓",
                    "message": "Select or Add Colleges to your Watchlist",
                    "name": "colleges",
                    "choices": existing_choices,
                }
                p = prompts.get_college_questions()
                p.insert(0, college_prompt)
                while True:
                    add_college_ans = prompt(p)
                    try:
                        if len(add_college_ans["new_college"]) > 255:
                            console.print("[bold red]College Name too long.[/]")
                            continue
                    except KeyError:
                        pass
                    break
                for c in add_college_ans["colleges"]:
                    if c != "Add it below!":
                        cd = {}
                        cd["ND"] = c
                        college_list.append(cd)
                try:
                    s = add_college_ans["deadline"]
                    cd = {}
                    cd[s[s.find("(") + 1 : s.find(")")]] = add_college_ans[
                        "new_college"
                    ].title()
                    college_list.append(cd)
                except KeyError:
                    pass
                more_college = prompt(
                    [
                        {
                            "type": "confirm",
                            "message": "Continue adding another college?",
                            "name": "more",
                            "default": True,
                        }
                    ]
                )
                add = more_college["more"]
            for c in college_list:
                name = list(c.values())[0]
                add_college(db, cursor, name)
            for c in college_list:
                for deadline, cname in c.items():
                    collegeID = helpers.get_single_record(
                        cursor, "CollegeID", "colleges", "CollegeName", cname
                    )
                    create_application(db, cursor, admnno, collegeID, deadline)
            display_student_tables(db, cursor, admnno)

        elif crud_ops["opr"] == "Remove a college":
            global add_rlist
            add_rlist, cid_list = True, []
            while add_rlist:
                
                while True:
                    remove_college_ans = prompt(
                        [
                            {
                                "type": "input",
                                "name": "cid",
                                "message": "Enter CollegeID of college to remove from watchlist",
                            }
                        ]
                    )
                    try:
                        cid_list.append(int(remove_college_ans["cid"]))
                    except:
                        console.print("[red]CollegeID not valid.[/]")
                        continue
                    cursor.execute(f"SELECT * FROM applications WHERE CollegeID = {remove_college_ans['cid']} AND AdmnNO = '{admnno}'")
                    record = cursor.fetchone()
                    if record == None:
                        console.print("[red]College not in watchlist.[/]")
                        continue
                    break
                more_college = prompt(
                    [
                        {
                            "type": "confirm",
                            "message": "Continue removing colleges from watchlist?",
                            "name": "more",
                            "default": True,
                        }
                    ]
                )
                add_rlist = more_college["more"]
            for cid in cid_list:
                delete_application(db, cursor, admnno, cid)
            display_student_tables(db, cursor, admnno)

        elif crud_ops["opr"] == "Request a LOR from a teacher":
            global add_lorlist
            add_lorlist, trno_list = True, []
            while add_lorlist:
                request_subject_ans = prompt(
                    [
                        {
                            "type": "list",
                            "name": "subj",
                            "message": "What subject does the teacher teach?",
                            "choices": [
                                "Accountancy",
                                "Biology",
                                "Biotechnology",
                                "BusinessStudies",
                                "Chemistry",
                                "ComputerScience",
                                "Economics",
                                "English",
                                "FineArts",
                                "Geography",
                                "Hindi",
                                "Mathematics",
                                "PerformingArts",
                                "PE",
                                "Physics",
                                "Political Science",
                                "Sanskrit",
                                "French",
                                "German",
                            ],
                        }
                    ]
                )
                subject = request_subject_ans["subj"]
                remove_college_ans = prompt(
                    [
                        {
                            "type": "list",
                            "name": "tname",
                            "message": "Choose your subject teacher.",
                            "choices": admin.get_existing_teachers(cursor, subject)
                        }
                    ]
                )
                try:
                    trno_list.append(re.findall("[T][0-9][0-9][0-9][0-9][0-9]", remove_college_ans["tname"])[0])
                except:
                    pass
                more_lor = prompt(
                    [
                        {
                            "type": "confirm",
                            "message": "Request another LOR from a teacher?",
                            "name": "more",
                            "default": True,
                        }
                    ]
                )
                add_lorlist = more_lor["more"]
            for trno in trno_list:
                lors.add_lor(db, cursor, trno, admnno)
            display_student_tables(db, cursor, admnno)

        elif crud_ops["opr"] == "Change the deadline of a college":
            while True:
                modify_deadline_ans = prompt(
                    [
                        {
                            "type": "input",
                            "name": "cid",
                            "message": "What's the CollegeID of the college you want to change dealdine of?",
                        },
                        {
                            "type": "list",
                            "name": "deadline",
                            "message": "What's your college applcation deadline",
                            "choices": [
                                "November first-week (US_EARLY1)",
                                "Mid-November (UK/US_EARLY2)",
                                "November End (US_UCs)",
                                "January first-week (UK/US_REGULAR)",
                                "Indian Private Colleges (INDIA_PRIV)",
                                "Not decided (ND)",
                            ],
                        },
                    ]
                )
                try:
                    cid = int(modify_deadline_ans["cid"])
                except ValueError:
                    console.print("[red]Invalid College ID.[/]")
                    continue
                cursor.execute(
                    "select Submitted from applications where CollegeID={} and AdmnNO='{}';".format(
                        cid, admnno
                    )
                )
                
                sstatus = cursor.fetchone()
                if sstatus == None:
                    console.print("[red]College not found[/]")
                    continue
                break

            try:
                s = modify_deadline_ans["deadline"]
                new_deadline = s[s.find("(") + 1 : s.find(")")]
                modify_application(db, cursor, admnno, cid, new_deadline, sstatus[0])
            except KeyError:
                pass
            display_student_tables(db, cursor, admnno)

        elif crud_ops["opr"] == "Change your application status for a college":
            while True:
                modify_deadline_ans = prompt(
                    [
                        {
                            "type": "input",
                            "name": "cid",
                            "message": "What's the CollegeID of the college you want to change status of?",
                        },
                        {
                            "type": "confirm",
                            "name": "status",
                            "message": "Have you submitted your application to this college?",
                            "default": True,
                        },
                    ]
                )
                try:
                    cid = int(modify_deadline_ans["cid"])
                except ValueError:
                    console.print("[red]Invalid College ID.[/]")
                    continue
                sstatus = int(modify_deadline_ans["status"])
                cursor.execute(
                    "select Deadline from applications where CollegeID={} and AdmnNO='{}';".format(
                        cid, admnno
                    )
                )
                
                deadline = cursor.fetchone()
                if deadline == None:
                    console.print("[red]College not found[/]")
                    continue
                break
            
            deadline = deadline[0]
            

            modify_application(
                db, cursor, admnno, cid, deadline, sstatus, change_status=True
            )
            display_student_tables(db, cursor, admnno)

        elif crud_ops["opr"] == "Delete your IntlApp account and exit.":
            delete_confirm = prompt(
                [
                    {
                        "type": "confirm",
                        "name": "delete",
                        "message": "Are you sure you want to delete all your applications and close your account? [IRREVERSIBLE]",
                        "default": False,
                    }
                ]
            )
            if delete_confirm["delete"]:
                cursor.execute("delete from students where AdmnNO='{}';".format(admnno))
                db.commit()
                delete_applications(db, cursor, admnno)
                delete_lors(db, cursor, admnno)
                console.print(
                    "\n😔 We're sorry to see you go.\n\n[italic red]Your account was deleted.[/]",
                    justify="center",
                )
                see_crud = False
                console.print("\n\n[dim]Exiting the appplication...[/]")

        elif crud_ops["opr"] == "Exit IntlApp Dashboard":
            see_crud = False
            console.print("\n\n[dim]Exiting the appplication...[/]")

        elif crud_ops['opr'] == 'Hide this prompt (to scroll up)':
            console.print(':eyes: The prompt is hidden.\n')
            show = str(input("Press enter to show it again:"))
            if len(show) == 0:
                see_crud = True

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

    while True:
        answers = prompt(questions)
        if len(answers["full_name"]) > 255:
            console.print("[bold red]Name too long.[/]")
            continue
        break
    # college prompt

    college_questions = prompts.get_college_questions()
    college_questions.insert(0, college_prompt)
    while True:
        canswers = prompt(college_questions)
        try:
            if len(canswers["new_college"]) > 255:
                console.print("[bold red]College Name too long.[/]")
                continue
        except KeyError:
            pass
        break
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

    new_user_query = "insert into students(AdmnNO, Name, Class, Stream, PSWDHASH) values ('{}', '{}', '{}', '{}', '{}');".format(
        admnno,
        answers["full_name"].title(),
        answers["clsec"],
        answers["stream"],
        pswd_hash,
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

    # create a new records in applications table
    for c in college_list:
        for deadline, cname in c.items():
            collegeID = helpers.get_single_record(
                cursor, "CollegeID", "colleges", "CollegeName", cname
            )
            create_application(db, cursor, admnno, collegeID, deadline)

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
