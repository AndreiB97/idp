import mysql.connector
import logging
import os
from time import sleep
from PyInquirer import prompt
from ast import literal_eval as make_tuple

db = None
retry_count = 0
logger = None

LANGUAGE = 'Review questions flagged for offensive language'
SCORE = 'Review questions flagged for low score'
SUBMITTED = 'Review user submitted questions'
POOL = 'Review current question pool'

EXIT = 'Exit'
NEXT = 'Next'
DELETE = 'Delete'
APPROVE = 'Approve'
FLAG = 'Flag as offensive'

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

    logger = logging.getLogger('Administrator')
    logger.setLevel(logging.INFO)


def action_dispatcher(action):
    if action == LANGUAGE:
        review_language()
    elif action == SCORE:
        review_score()
    elif action == SUBMITTED:
        review_submitted()
    elif action == POOL:
        review_pool()
    elif action == EXIT:
        exit(0)
    else:
        logger.warning(f'Unsupported action {action}')


def review_score():
    cursor = db.cursor()
    cursor.callproc('')

    for result in cursor.stored_results():
        process_pool_result(result)


def review_pool():
    cursor = db.cursor()
    cursor.callproc('get_question_pool')

    for result in cursor.stored_results():
        process_pool_result(result)


def process_pool_result(result):
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
            choice_tuple = make_tuple(choice)
            res = process_pool_item(choice_tuple)

            if res == DELETE:
                rows.remove(choice_tuple)

    print('No rows left')


def process_pool_item(item):
    action = prompt([{
        'type': 'list',
        'name': 'action',
        'message': str(item),
        'choices': [
            DELETE,
            EXIT
        ]
    }])['action']

    cursor = db.cursor()

    if action == DELETE:
        cursor.callproc('delete_question_from_pool', (item[0],))

        db.commit()

        return DELETE
    elif action == EXIT:
        return EXIT
    else:
        logger.error(f'Unsupported action {action}')


def review_submitted():
    cursor = db.cursor()
    cursor.callproc('get_user_submitted_questions')

    for result in cursor.stored_results():
        process_user_submitted_result(result)


def review_language():
    cursor = db.cursor()
    cursor.callproc('get_flagged_offensive_questions')

    for result in cursor.stored_results():
        process_offensive_language_result(result)


def process_user_submitted_result(result):
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
            choice_tuple = make_tuple(choice)
            res = process_user_submitted_item(choice_tuple)

            if res == APPROVE or res == DELETE or res == FLAG:
                rows.remove(choice_tuple)

    print('No rows left')


def process_user_submitted_item(item):
    action = prompt([{
        'type': 'list',
        'name': 'action',
        'message': str(item),
        'choices': [
            APPROVE,
            FLAG,
            DELETE,
            EXIT
        ]
    }])['action']

    cursor = db.cursor()

    if action == DELETE:
        cursor.callproc('delete_user_submitted_question', (item[0],))

        db.commit()

        return DELETE
    elif action == APPROVE:
        cursor.callproc('approve_question', (item[0],))

        db.commit()

        return APPROVE
    elif action == FLAG:
        cursor.callproc('flag_user_submitted_question', (item[0],))

        db.commit()

        return FLAG
    elif action == EXIT:
        return EXIT
    else:
        logger.error(f'Unsupported action {action}')


def process_offensive_language_result(result):
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
            choice_tuple = make_tuple(choice)
            res = process_offensive_language_item(choice_tuple)

            if res == DELETE:
                rows.remove(choice_tuple)

    print('No rows left')


def process_offensive_language_item(item):
    action = prompt([{
        'type': 'list',
        'name': 'action',
        'message': str(item),
        'choices': [
            DELETE,
            EXIT
        ]
    }])['action']

    cursor = db.cursor()

    if action == DELETE:
        cursor.callproc('delete_flagged_offensive_question', (item[0],))

        db.commit()

        logger.info(f'Deleted {item} for offensive language')

        return DELETE
    elif action == EXIT:
        return EXIT
    else:
        logger.error(f'Unsupported action {action}')


def cli():
    while True:
        answer = prompt([MAIN_MENU])
        action_dispatcher(answer['action'])


if __name__ == '__main__':
    init_logger()
    connect_to_db()
    cli()
