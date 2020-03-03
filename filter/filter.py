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


if __name__ == '__main__':
    init_logger()
    connect_to_db()
    filter_user_submitted_questions()
