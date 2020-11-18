from PyInquirer import Separator


def get_student_questions():
    questions = [
        {
            'type': 'input',
            'name': 'full_name',
            'message': 'What\'s your name',
        },
        {
            'type': 'input',
            'name': 'clsec',
            'message': 'What\'s your class and section',
            'default': '12I'
        },
        {
            'type': 'list',
            'name': 'stream',
            'message': 'What\'s your stream ?',
            'choices': ['PCB', 'PCMC', 'PCMB', 'PCME', 'COMM.', 'HUMA.', 'OTHER'],
        },
    ]
    return questions


def get_admin_questions():
    questions = [
        {
            'type': 'input',
            'name': 'full_name',
            'message': 'What\'s your name',
        },
        {
            'type': 'confirm',
            'name': 'is_counselor',
            'message': 'Are you the counselor?',
            'default': False
        },
        {
            'type': 'list',
            'name': 'subject',
            'message': 'What subject do you teach?',
            'choices': ['Accountancy', 'Biology', 'Biotechnology', 'BusinessStudies', 'Chemistry', 'ComputerScience', 'Economics', 'English', 'FineArts', 'Geography', 'Hindi', 'Mathematics', 'PerformingArts', 'PE', 'Physics', 'Political Science', 'Sanskrit' 'French', 'German'],
            'when': lambda answers: not answers['is_counselor']
        },
    ]
    return questions


def get_college_questions():
    college_questions = [
        {
            'type': 'confirm',
            'name': 'add_new',
            'message': 'Add a new college to your Watchlist?',
            'default': True
        },
        {
            'type': 'input',
            'name': 'new_college',
            'message': 'What\'s your college/university name',
            'when': lambda answers: answers['add_new']
        },
        {
            'type': 'list',
            'name': 'deadline',
            'message': 'What\'s your college applcation deadline',
            'choices': ['November first-week (US_EARLY1)', 'Mid-November (UK/US_EARLY2)', 'November End (US_UCs)', 'January first-week (UK/US_REGULAR)', 'Not decided (ND)'],
            'when': lambda answers: answers['add_new']
        }
    ]
    return college_questions
