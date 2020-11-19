import os
import bcrypt
import sys
from dotenv import load_dotenv
import mysql.connector as mysql
from rich.console import Console
from rich.text import Text
from pyfiglet import Figlet
import user, admin, notifs
from getpass import getpass
import helpers
from PyInquirer import prompt

def main():
    load_dotenv(verbose=True)
    try:
        import colorama

        colorama.init()
    except ImportError:
        colorama = None
    try:
        from termcolor import colored
    except ImportError:
        colored = None

    console = Console()
    init = Text()
    init.append("Starting Application \n\n", style="italic")
    console.print(init)
    font = Figlet(font="larry3d")
    # console.print(font.renderText('IntlApp Dashboard - CLI'), style='bold green')
    text = Text(justify="center").assemble(
        (font.renderText("IntlApp"), "bold green"),
        (font.renderText("Dashboard"), "bold yellow"),
    )
    console.print(text, justify="full")

    ps = 3306 if os.name == "nt" else "3306"

    db = mysql.connect(
        host="localhost",
        user=os.getenv("DATABASE_USERNAME"),
        password=os.getenv("DATABASE_PASSWORD"),
        port=ps,
        database=os.getenv("DATABASE_NAME"),
    )
    if db:
        cursor = db.cursor(buffered=True)
        cursor.execute("use {};".format(os.getenv("DATABASE_NAME")))
        console.print(
            "Connection [green][b]successful[/b][/green][blink]...[/blink]\n\n :gear: Initialising Tables\n\n"
        )
        # init and check for tables: user, counselor, teacher, sessions ...
        user.student_create_table(cursor)
        admin.teacher_create_table(cursor)
        user.college_create_table(cursor)
        user.apps_create_table(cursor)
        notifs.create_table(cursor)

        login = False
        global inp
        while not login:
            console.print("🔐 Login as ? \n\n (1) Counselor / Teacher \n (2) Student")
            inp = str(input("\n\nPlease enter number to login as: "))
            if inp == "1":
                global trno
                global exist
                global is_counselor
                console.print("Enter the [b]Admin Credentials[/b]\n")
                trno = str(input("Enter your Staff/Teacher ID:"))
                console.print("\n\n🔎 Searching for existing record in the database...")
                is_counselor, exist = False, False
                cursor.execute("select IS_COUNSELOR from teachers where TrNO='{}';".format(trno))
                output = cursor.fetchone()
                if output != None:
                    exist, is_counselor = True, True
                if exist:
                    console.print(":+1: Existing Record found.\n", justify="center")
                    console.print("[b]Login to your account[/b]\n", justify="center")
                    password = getpass(prompt="Enter your password: ")
                    password = password.encode("ascii")
                    pswd_hash = admin.get_pswdhash(cursor, trno)
                    if bcrypt.checkpw(password, pswd_hash):
                        login = True
                        console.print("\n[u green]Password verified.[/u green]\n\n")
                    else:
                        console.print("\n[u]Password [red]not verified.[/red][/u]\n\n")
                else:
                    console.print(":pensive: Record not found.\n\n")
                    confirm = [
                        {
                            "type": "confirm",
                            "message": "Would you like to create a new account",
                            "name": "verify",
                            "default": True,
                        },
                    ]
                    answers = prompt(confirm)
                    if not answers["verify"]:
                        console.print(
                            "Uh-oh! Thank you for using IntlApp Dashboard.\n\n[i]Exiting...[/i]"
                        )
                        exit()
                    else:
                        console.print(
                            "🙈 [i green]We do not store your passwords.[/i green]"
                        )
                        password = getpass(prompt="Enter a new password: ")
                        password = password.encode("ascii")
                        hsh = bcrypt.hashpw(
                            password, os.getenv("BCRYPT_SALT").encode("ascii")
                        )
                        ok, is_c = admin.teacher_create_prompt(
                            db, cursor, trno.upper(), hsh.decode("ascii")
                        )
                        if ok == "ok":
                            login = True
                            if is_c == 'ok':
                                admin.counselor_dash(cursor, trno.upper())
                            print("todo...")
                        else:
                            break
            elif inp == "2":
                global admnno
                global exists
                admnno = str(input("Enter your admission number: "))
                console.print("🔎 Searching for existing record in the database...")
                exists = False
                cursor.execute(
                    "select * from students where AdmnNO='{}';".format(admnno)
                )
                output = cursor.fetchone()
                if output != None:
                    exists = True
                if exists:
                    console.print(
                        ":+1: Existing Record found.\n\n[u green] Login to your account[/u green]\n"
                    )
                    password = getpass(prompt="Enter your password: ")
                    password = password.encode("ascii")
                    pswd_hash = user.get_pswdhash(cursor, admnno)
                    if bcrypt.checkpw(password, pswd_hash):
                        login = True
                        console.print("\n[u green]Password verified.[/u green]\n\n")
                    else:
                        console.print("\n[u]Password [red]not verified.[/red][/u]\n\n")
                else:
                    console.print(":pensive: Record not found.\n\n")
                    confirm = [
                        {
                            "type": "confirm",
                            "message": "Would you like to create a new account",
                            "name": "verify",
                            "default": True,
                        },
                    ]
                    answers = prompt(confirm)
                    if not answers["verify"]:
                        console.print(
                            "Uh-oh! Thank you for using IntlApp Dashboard.\n\n[i]Exiting...[/i]"
                        )
                        exit()
                    else:
                        console.print(
                            "🙈 [i green]We do not store your passwords.[/i green]"
                        )
                        password = getpass(prompt="Enter a new password: ")
                        password = password.encode("ascii")
                        hsh = bcrypt.hashpw(
                            password, os.getenv("BCRYPT_SALT").encode("ascii")
                        )
                        ok = user.student_create_prompt(
                            db, cursor, admnno.upper(), hsh.decode("ascii")
                        )
                        if ok == "ok":
                            login = True
                            print("todo...")
                        else:
                            break
            else:
                print("catch something maybe")
        if login and inp == "2":
            console.print("✅ Student Login Successful")
            user.login_display_student(db, cursor, admnno)
        elif login and inp == "1":
            console.print("✅ Teacher Login Successful")
            if is_counselor:
                admin.counselor_dash(cursor, trno.upper())
            else:
                print('todo')
    else:
        console.print("⚠️  Something went wrong... Please try again.")
    # except:
    #     console.print('There was some error connecting to the database.\n\n[bold red]⚠️  Something went wrong... Please try again.[/bold red]')
    #     exit


if __name__ == "__main__":
    console = Console()
    try:
        main()
    except:
        # halt traceback for sometime
        console.print_exception()
        console.print("\n[bold red]Exiting gracefully...[/]\n")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
