from rich.table import Table
from rich.panel import Panel
import os, rich
import mysql.connector as mysql
import re


def check_table_exists(table_name):
    db = mysql.connect(
        host="localhost",
        user=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        port="3306",
        database=os.getenv("DATABASE_NAME"),
    )

    cur = db.cursor()
    try:
        cur.execute("SHOW TABLES")
        if (table_name,) in cur.fetchall():
            print("Loading Table...")
            return True
        else:
            return False
    except:
        print("Some Error occurred.")


def deadlines_panel():
    table = Table(show_header=True, header_style="bold cyan", show_footer=False)
    table.box = rich.box.MINIMAL
    table.title = "[not italic]⏰[/] Deadline Reference"
    table.add_column("Key", justify="center")
    table.add_column("Timeline Description.")
    table.add_row("[bold]US_EARLY1[/]", "[dim]November first-week[/]")
    table.add_row("[bold]UK/US_EARLY2[/]", "[dim]Mid-November[/]")
    table.add_row("[bold]US_UCs[/]", "[dim]November End[/]")
    table.add_row("[bold]UK/US_REGULAR[/]", "[dim]January first-week[/]")
    table.add_row("[bold]ND[/]", "[dim]Not Decided[/]")
    return Panel(table)


def get_single_record(cursor, cname, tname, conditional_cname, conditional_cvalue):
    cursor.execute(
        "select {} from {} where {}='{}';".format(
            cname, tname, conditional_cname, conditional_cvalue
        )
    )
    output = cursor.fetchone()
    return output[0]

def check_trno(trno):
    if len(trno) == 6:
        if trno[0] == "T" and trno[1:6].isdigit():
            return True
    else:
        return False

def check_admnno(admnno):
    admnno = admnno.upper()
    if re.match("^[REV][0-9][0-9][0-9][0-9][0-9]$", admnno):
        return True
    else:
        return False

def check_clsec(clsec):
    clsec = clsec.upper()
    if re.match("^1[12][A-Z]$", clsec):
        return True
    else:
        return False
