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
NEXT = 'Next'

BATCH_SIZE = 5

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
        review_language()
        cli()
    elif action == SCORE:
        # TODO
        logger.error('Not implemented')
    elif action == SUBMITTED:
        # TODO
        logger.error('Not implemented')
    elif action == POOL:
        # TODO
        logger.error('Not implemented')
    elif action == EXIT:
        return
    else:
        logger.warning(f'Unsupported action {action}')


def review_language():
    cursor = db.cursor()
    cursor.callproc('get_flagged_offensive_questions')

    for result in cursor.stored_results():
        process_result(result)


def process_result(result):
    rows = result.fetchmany(size=BATCH_SIZE)

    while rows:
        choices = [str(row) for row in rows]
        choices.append('Next')
        choices.append('Exit')

        choice = prompt([{
            'type': 'rawlist',
            'name': 'item',
            'message': '',
            'choices': choices
        }])['item']

        if choice == EXIT:
            return
        elif choice == NEXT:
            rows = result.fetchmany(size=BATCH_SIZE)
        else:
            # TODO prompt for selected row
            print(choice, flush=True)

    print('No rows left')


def cli():
    answer = prompt([MAIN_MENU])
    action_dispatcher(answer['action'])


if __name__ == '__main__':
    init_logger()
    connect_to_db()
    cli()
