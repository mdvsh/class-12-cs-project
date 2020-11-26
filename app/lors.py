import os
import rich
import mysql.connector as mysql

def create_table(cursor):
    console = rich.console.Console()
    query = "create table if not exists lors(AdmnNO CHAR(6) NOT NULL, TrNO CHAR(6) NOT NULL, Submitted bool default False not null);"
    this_dir, this_filename = os.path.split(__file__)
    LOG_PATH = os.path.join(this_dir, "logs", "logs.txt")
    to_print = "[ERROR]: COULD NOT CREATE LORS TABLE"
    try:
        cursor.execute(query)
        to_print = "[CREATE] TABLE LORS"
    except Exception:
        console.print(":bulb: Existing lor table found ")
        to_print = "[DB ERROR]: EXISTING TABLE FOUND"

    with open(LOG_PATH, "a") as log_file:
        log_file.write(to_print + "\n")