import logging
import mysql.connector.errors as errors
from PyInquirer import prompt
from time import sleep
from ast import literal_eval as make_tuple
from db_connection.connect_helper import connect_to_db, set_logger, SLEEP_AMOUNT

db = None
retry_count = 0
logger = None

QUESTION_POOL_HEADER = '(ID, Answer 1, Answer 2, Answer 1 count, Answer 2 count, Score, Views, Priority)'
FLAGGED_OFFENSIVE_QUESTIONS_HEADER = '(ID, Answer 1, Answer 2)'
FLAGGED_LOW_SCORE_QUESTIONS_HEADER = '(ID, Answer 1, Answer 2, Answer 1 count, Answer 2 count, Score, Views)'
USER_SUBMITTED_QUESTIONS_HEADER = '(ID, Answer 1, Answer 2)'

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
    global retry_count

    cursor = db.cursor()

    while True:
        try:
            cursor.callproc('get_flagged_low_score_questions')

            break
        except errors.ProgrammingError:
            if retry_count < 5:
                logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                sleep(SLEEP_AMOUNT)

                retry_count -= - 1
                logger.warn(f'Retrying attempt #{retry_count}')
                continue
            else:
                logger.error('Maximum number of retries reached.')
                raise

    retry_count = 0

    for result in cursor.stored_results():
        process_score_result(result)


def process_score_result(result):
    rows = result.fetchmany(size=BATCH_SIZE)

    while rows:
        choices = [str(row) for row in rows]
        choices.append('Next')
        choices.append('Exit')

        choice = prompt([{
            'type': 'rawlist',
            'name': 'item',
            'message': FLAGGED_LOW_SCORE_QUESTIONS_HEADER,
            'choices': choices
        }])['item']

        if choice == EXIT:
            return
        elif choice == NEXT:
            rows = result.fetchmany(size=BATCH_SIZE)
        else:
            choice_tuple = make_tuple(choice)
            res = process_score_item(choice_tuple)

            if res == DELETE:
                rows.remove(choice_tuple)

    print('No rows left')


def process_score_item(item):
    global retry_count

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
        while True:
            try:
                cursor.callproc('delete_flagged_low_score_question', (item[0],))

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -= - 1
                    logger.warn(f'Retrying attempt #{retry_count}')
                    continue
                else:
                    logger.error('Maximum number of retries reached.')
                    raise

        retry_count = 0
        db.commit()

        return DELETE
    elif action == EXIT:
        return EXIT
    else:
        logger.error(f'Unsupported action {action}')


def review_pool():
    global retry_count

    cursor = db.cursor()

    while True:
        try:
            cursor.callproc('get_question_pool')

            break
        except errors.ProgrammingError:
            if retry_count < 5:
                logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                sleep(SLEEP_AMOUNT)

                retry_count -= - 1
                logger.warn(f'Retrying attempt #{retry_count}')
                continue
            else:
                logger.error('Maximum number of retries reached.')
                raise

    retry_count = 0

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
            'message': QUESTION_POOL_HEADER,
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
    global retry_count

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
        while True:
            try:
                cursor.callproc('delete_question_from_pool', (item[0],))

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -= - 1
                    logger.warn(f'Retrying attempt #{retry_count}')
                    continue
                else:
                    logger.error('Maximum number of retries reached.')
                    raise

        retry_count = 0

        db.commit()

        return DELETE
    elif action == EXIT:
        return EXIT
    else:
        logger.error(f'Unsupported action {action}')


def review_submitted():
    global retry_count

    cursor = db.cursor()

    while True:
        try:
            cursor.callproc('get_user_submitted_questions')

            break
        except errors.ProgrammingError:
            if retry_count < 5:
                logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                sleep(SLEEP_AMOUNT)

                retry_count -= - 1
                logger.warn(f'Retrying attempt #{retry_count}')
                continue
            else:
                logger.error('Maximum number of retries reached.')
                raise

    retry_count = 0

    for result in cursor.stored_results():
        process_user_submitted_result(result)


def review_language():
    global retry_count

    cursor = db.cursor()

    while True:
        try:
            cursor.callproc('get_flagged_offensive_questions')

            break
        except errors.ProgrammingError:
            if retry_count < 5:
                logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                sleep(SLEEP_AMOUNT)

                retry_count -= - 1
                logger.warn(f'Retrying attempt #{retry_count}')
                continue
            else:
                logger.error('Maximum number of retries reached.')
                raise

    retry_count = 0

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
            'message': USER_SUBMITTED_QUESTIONS_HEADER,
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
    global retry_count

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
    ret = None

    while True:
        try:
            if action == DELETE:
                cursor.callproc('delete_user_submitted_question', (item[0],))

                db.commit()

                ret = DELETE
            elif action == APPROVE:
                cursor.callproc('approve_question', (item[0],))

                db.commit()

                ret = APPROVE
            elif action == FLAG:
                cursor.callproc('flag_user_submitted_question', (item[0],))

                db.commit()

                ret = FLAG
            elif action == EXIT:
                ret = EXIT
            else:
                logger.error(f'Unsupported action {action}')

            break
        except errors.ProgrammingError:
            if retry_count < 5:
                logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                sleep(SLEEP_AMOUNT)

                retry_count -= - 1
                logger.warn(f'Retrying attempt #{retry_count}')
                continue
            else:
                logger.error('Maximum number of retries reached.')
                raise

    retry_count = 0

    return ret


def process_offensive_language_result(result):
    rows = result.fetchmany(size=BATCH_SIZE)

    while rows:
        choices = [str(row) for row in rows]
        choices.append('Next')
        choices.append('Exit')

        choice = prompt([{
            'type': 'rawlist',
            'name': 'item',
            'message': FLAGGED_OFFENSIVE_QUESTIONS_HEADER,
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
    global retry_count

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
        while True:
            try:
                cursor.callproc('delete_flagged_offensive_question', (item[0],))

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -= - 1
                    logger.warn(f'Retrying attempt #{retry_count}')
                    continue
                else:
                    logger.error('Maximum number of retries reached.')
                    raise

        retry_count = 0
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
    set_logger(logger)
    db = connect_to_db()
    cli()
