import os, bcrypt, sys
from dotenv import load_dotenv
import mysql.connector as mysql
from rich.console import Console
from rich.text import Text
from pyfiglet import Figlet
import user
from getpass import getpass

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
    init.append('Starting Application \n\n', style='italic')
    console.print(init)
    font = Figlet(font='larry3d')
    # console.print(font.renderText('IntlApp Dashboard - CLI'), style='bold green')
    text = Text(justify='center').assemble((font.renderText('IntlApp'), 'bold green'), (font.renderText('Dashboard'), 'bold yellow'))
    console.print(text)

    ps = 3306 if os.name == 'nt' else '3306'

    db = mysql.connect(
        host='localhost',
        user=os.getenv('DATABASE_USERNAME'),
        password=os.getenv('DATABASE_PASSWORD'),
        port=ps,
        database=os.getenv('DATABASE_NAME')
    )
    if db:
        cursor = db.cursor(buffered=True)
        cursor.execute('use {};'.format(os.getenv('DATABASE_NAME')))
        console.print('Connection [green][b]successful[/b][/green][blink]...[/blink]\n\n :gear: Initialising Tables\n\n')
        # init and check for tables: user, counselor, teacher, sessions ...
        user.student_create_table(cursor)
        # admin.admin_create_table(cursor)
        login = False
        while not login:
            console.print('🔐 Login as ? \n\n (1) Counselor / Teacher \n (2) Student')
            inp = str(input('\n\nPlease enter number to login as: '))
            if inp == '1':
                console.print('Enter the [b]Admin Credentials [/b]')
            elif inp == '2':
                global admno
                admno = str(input('Enter your admission number: '))
                console.print('🔎 Searching for existing record in the database...')
                if user.exists(cursor, admno):
                    # ask for password, unhash and confirm login = True
                    console.print(':+1: Existing Record found.\n[bold green] Login to your account[/bold green]\n\n')
                    password = getpass(prompt='Enter your password: ')
                    password = password.encode('ascii')
                    pswd_hash = user.get_pswdhash(cursor, admno)
                    if bcrypt.checkpw(password, pswd_hash):
                        login = True
                        console.print('\n[u green]Password verified.[/u green]\n\n')
                    else:
                        console.print('\n[u]Password [red]not verified.[/red][/u]\n\n')
                else:
                    # create new user, ask for password, ask for details then show table to confirm reg and login = True
                    console.print(':pensive: Record not found.\n\n')
                    new = str(input('Would you like to create an account [y/n] ? '))
                    if new[0] == 'n':
                        console.print("Uh-oh! Thank you for using IntlApp Dashboard.\n\n[i]Exiting...[/i]")
                        exit()
                    else:
                        console.print('🙈 [i green]We do not store your passwords.[/i green]')
                        # admnno = str(input('Enter Admission Number: '))
                        password = getpass(prompt='Enter a new password: ')
                        password = password.encode('ascii')
                        hsh = bcrypt.hashpw(password, os.getenv('BCRYPT_SALT').encode('ascii'))
                        # send admnno and pswd hash to creation function
                        ok = user.student_create_prompt(db, cursor, admno.upper(), hsh.decode('ascii'))
                        if ok:
                            login = True
                            print('todo...')
            else:
                print('catch something maybe')
        if login:
            console.print('✅ Login Successful')
    else:
        console.print('⚠️  Something went wrong... Please try again.')
    # except:
    #     console.print('There was some error connecting to the database.\n\n[bold red]⚠️  Something went wrong... Please try again.[/bold red]')
    #     exit

    # prompt starts now

if __name__ == '__main__':
    console = Console()
    try:
        main()
    except KeyboardInterrupt or EOFError:
        console.print('\n\n\n[bold red]Exiting gracefully...[/]')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)