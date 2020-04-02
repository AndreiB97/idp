import os
import logging
import schedule
from time import sleep
from profanity_check import predict_prob
from db_connection.connect_helper import set_logger, connect_to_db

# TODO catch mysql no procedure exceptions and retry

db = None
logger = None


def init_logger():
    global logger

    logger = logging.Logger(name='Filter')
    logger.setLevel(logging.INFO)


def filter_profanity(question_id, ans1, ans2, cursor):
    profanity_probabilities = predict_prob([ans1, ans2])

    for probability in profanity_probabilities:
        if probability > 0.5:
            cursor.callproc('flag_user_submitted_question', (question_id,))
            db.commit()

            return True

    return False


def scan_user_submitted_questions():
    cursor = db.cursor()
    cursor.callproc('get_user_submitted_questions')

    for result in cursor.stored_results():
        for row in result.fetchall():
            question_id = row[0]
            ans1 = row[1]
            ans2 = row[2]

            res = filter_profanity(question_id, ans1, ans2, cursor)

            if res is True:
                logger.info(f'Flagging {row} for profanity')


def get_rerun_timer():
    timer_minutes_total = 0

    timer_minutes = os.environ.get('FILTER_RERUN_TIMER_MINUTES')
    timer_hours = os.environ.get('FILTER_RERUN_TIMER_HOURS')
    timer_days = os.environ.get('FILTER_RERUN_TIMER_DAYS')

    try:
        if timer_minutes is not None:
            timer_minutes_total += int(timer_minutes)
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_MINUTES is not int')
        logger.debug(f'FILTER_RERUN_TIMER_MINUTES={timer_minutes}')

    try:
        if timer_hours is not None:
            timer_minutes_total += int(timer_hours) * 60
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_HOURS is not int')
        logger.debug(f'FILTER_RERUN_TIMER_HOURS={timer_hours}')

    try:
        if timer_days is not None:
            timer_minutes_total += int(timer_days) * 24 * 60
    except TypeError:
        logger.warning('Type of FILTER_RERUN_TIMER_DAYS is not int')
        logger.debug(f'FILTER_RERUN_TIMER_DAYS={timer_days}')

    if timer_minutes_total == 0:
        timer_minutes_total = 24 * 60
        logger.debug('Using default timer value of 24 hours')

    return timer_minutes_total


def filter_low_score_question(question_id, views, score, cursor):
    if views > 100 and score < views * 0.10:
        cursor.callproc('flag_low_score_question', (question_id,))
        db.commit()

        return True

    return False


def filter_priority(question_id, views, priority, cursor):
    if views < 100 and priority == 0:
        cursor.callproc('give_priority', (question_id,))
        db.commit()

        return True
    elif views >= 100 and priority == 1:
        cursor.callproc('remove_priority', (question_id,))
        db.commit()

        return True

    return False


def scan_question_pool():
    cursor = db.cursor()
    cursor.callproc('get_question_pool')

    for result in cursor.stored_results():
        for row in result.fetchall():
            question_id = row[0]
            score = row[5]
            views = row[6]
            priority = row[7]

            res = filter_priority(question_id, views, priority, cursor)

            if res is True:
                logger.info(f'Changed priority for {row}')
                break

            res = filter_low_score_question(question_id, views, score, cursor)

            if res is True:
                logger.info(f'Flagging {row} for low score')


if __name__ == '__main__':
    init_logger()
    set_logger(logger)
    db = connect_to_db()
    timer_minutes = get_rerun_timer()

    schedule.every(timer_minutes).minutes.do(scan_question_pool)
    schedule.every(timer_minutes).minutes.do(scan_user_submitted_questions)

    while True:
        schedule.run_pending()
        sleep(1)