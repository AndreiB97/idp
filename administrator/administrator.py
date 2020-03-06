import mysql.connector
import logging
import os
from time import sleep
from PyInquirer import prompt

db = None
retry_count = 0
logger = None

LANGUAGE = 'Review questions flagged for offensive language'
SCORE = 'Review questions flagged for low score'
SUBMITTED = 'Review user submitted questions'
POOL = 'Review current question pool'
EXIT = 'Exit'

MAIN_MENU = {
    'type': 'list',
    'name': 'action',
    'message': 'Select an action',
    'choices': [
        {
            'name': LANGUAGE
        },
        {
            'name': SCORE
        },
        {
            'name': SUBMITTED
        },
        {
            'name': POOL
        },
        {
            'name': EXIT
        }
    ]
}


def connect_to_db():
    global db, retry_count

    try:
        db = mysql.connector.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            passwd=os.environ['DB_PASS'],
            database=os.environ['DB_NAME']
        )

        logger.info('Connected to DB')
    except mysql.connector.errors.InterfaceError:
        if retry_count < 5:
            retry_count -=- 1
            logger.warning(f'Unable to connect to DB. Retry #{retry_count}.')
            sleep(1)
            connect_to_db()
        else:
            logger.error('Maximum number of retries reached.')
            raise


def init_logger():
    global logger

    logger = logging.getLogger('Filter')
    logger.setLevel(logging.INFO)


def action_dispatcher(action):
    if action == LANGUAGE:
        pass
    elif action == SCORE:
        pass
    elif action == SUBMITTED:
        pass
    elif action == POOL:
        pass
    elif action == EXIT:
        pass
    else:
        logger.warning(f'Unsupported action {action}')


def cli():
    answer = prompt([MAIN_MENU])
    action_dispatcher(answer['action'])


if __name__ == '__main__':
    init_logger()
    connect_to_db()
    cli()
