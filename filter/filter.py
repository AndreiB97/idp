import mysql.connector
import os
import logging
from time import sleep
from profanity_check import predict_prob

db = None
retry_count = 0
logger = None


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


def filter_user_submitted_questions():
    cursor = db.cursor()
    cursor.callproc('get_user_submitted_questions')

    for result in cursor.stored_results():
        for row in result.fetchall():
            profanity_probabilities = predict_prob([row[1], row[2]])
            for probability in profanity_probabilities:
                if probability > 0.5:
                    logger.info(f'Flagging {row} for profanity')
                    cursor.callproc('flag_user_submitted_question', (row[0], ))
                    db.commit()
                    break


def get_rerun_timer():
    timer = 0

    rerun_seconds = os.environ.get('FILTER_RERUN_TIMER_SECONDS')
    rerun_minutes = os.environ.get('FILTER_RERUN_TIMER_MINUTES')
    rerun_hours = os.environ.get('FILTER_RERUN_TIMER_HOURS')
    rerun_days = os.environ.get('FILTER_RERUN_TIMER_DAYS')

    try:
        if rerun_seconds is not None:
            timer += int(rerun_seconds)
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_SECONDS is not int')
        logger.debug(f'FILTER_RERUN_TIMER_SECONDS={rerun_seconds}')

    try:
        if rerun_minutes is not None:
            timer += int(rerun_minutes) * 60
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_MINUTES is not int')
        logger.debug(f'FILTER_RERUN_TIMER_MINUTES={rerun_minutes}')

    try:
        if rerun_hours is not None:
            timer += int(rerun_hours) * 60 * 60
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_HOURS is not int')
        logger.debug(f'FILTER_RERUN_TIMER_HOURS={rerun_hours}')

    try:
        if rerun_days is not None:
            timer += int(rerun_days) * 24 * 60 * 60
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_DAYS is not int')
        logger.debug(f'FILTER_RERUN_TIMER_DAYS={rerun_days}')

    if timer == 0:
        timer = 24 * 60 * 60
        logger.debug(f'Using default timer value {timer}')

    return timer


def filter_low_score_questions():
    cursor = db.cursor()
    cursor.callproc('get_question_pool')

    for result in cursor.stored_results():
        for row in result.fetchall():
            id = row[0]
            score = row[5]
            views = row[6]
            if views > 100 and score < views * 0.10:
                cursor.callproc('flag_low_score_question', (id, ))
                logger.info(f'Flagging {row} for low score')
                db.commit()


if __name__ == '__main__':
    init_logger()
    connect_to_db()

    timer = get_rerun_timer()

    while True:
        filter_user_submitted_questions()
        filter_low_score_questions()
        sleep(timer)
