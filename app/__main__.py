import argparse, os
from dotenv import load_dotenv
import mysql.connector as mysql

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-u', '--user', help='Type of user: (1) Counselor/Teacher (2) Student')
    # args = parser.parse_args()
    load_dotenv(verbose=True)
    try:
        db = mysql.connect(
            host='localhost',
            user=os.getenv('DATABASE_USERNAME'),
            password=os.getenv('DATABASE_PASSWORD'),
            port='3306',
        )
        if db:
            print('Connection Successful...')
    except:
        print('There was some error connecting to the your dashboard.')

if __name__ == '__main__':
    main()