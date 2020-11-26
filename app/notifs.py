import os
import rich
from PyInquirer import prompt, Separator
import mysql.connector as mysql
from rich.columns import Columns
from rich.panel import Panel


def create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists notifications(GroupID INT NOT NULL, NotifID int not null auto_increment, Audience varchar(5) not null, Date DATE not null, Description TEXT not null, primary key(NotifID));"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE NOTIFICATIONS TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE NOTIFICATIONS"
    except Exception:
        console.print(":bulb: Existing notifications table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")


# todo: change color of notificaitons based on time left to event: RED (<=2 DAYS), YELLOW (<=10 DAYS), GREEN (else)


def panel(cursor, stream, panel=True, admin=False):
    console = rich.console.Console()
    if admin:
        query = "select DISTINCT Description, date_format(Date, '%d %M %Y') from notifications;"
    else:
        query = "select Description, date_format(Date, '%d %M %Y') from notifications where Audience='{}';".format(
            stream
        )
    cursor.execute(query)
    notifications = cursor.fetchall()
    table = rich.table.Table(
        show_header=True, header_style="bold green", show_footer=False
    )
    table.box = rich.box.MINIMAL
    table.title = (
        "[not italic]🔔[/] Notifications / Scheduled Sessions "
        if admin
        else "[not italic]🔔[/] Your Notifications"
    )
    table.add_column("Date of Action", justify="center")
    table.add_column("Description")
    if len(notifications) != 0:
        for notif in notifications:
            table.add_row(f"[dim]{notif[1]}[/]", f"{notif[0]}")
    else:
        if admin:
            table.add_row(":+1:", "You have posted no notifications / sessions.")
        else:
            table.add_row(":+1:", "You have no pending notifications.")

    return Panel(table) if panel else console.print(table)
