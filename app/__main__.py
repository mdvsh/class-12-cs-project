import argparse, os, rich, bcrypt
from dotenv import load_dotenv
import mysql.connector as mysql
from rich.console import Console
from rich.text import Text
from pyfiglet import Figlet
import user

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--user', help='Type of user: (1) Counselor/Teacher (2) Student')
    # args = parser.parse_args()
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

    try:
        db = mysql.connect(
            host='localhost',
            user=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            port=ps,
            database=os.getenv('DATABASE_NAME')
        )
        if db:
            cursor = db.cursor()
            cursor.execute('use {};'.format(os.getenv('DATABASE_NAME')))
            console.print('Connection [green][b]successfull[/b][/green][blink]...[/blink]\n\nSetting up tables')
            # init and check for tables: user, counselor, teacher, sessions ...
            user.student_create_table(cursor)

            
    except:
        console.print('There was some error connecting to the database.\n\n[bold red]Please make sure the database exists.[/bold red]')
        exit

    # login inquirer


if __name__ == '__main__':
    main()