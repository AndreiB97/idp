import os
import logging
import mysql.connector
from time import sleep

db = None
retry_count = 0
SLEEP_AMOUNT = 3
logger = logging.Logger(name="DB connector helper")


def set_logger(new_logger):
    global logger
    logger = new_logger


def connect_to_db():
    global db, retry_count, logger

    while True:
        try:
            db = mysql.connector.connect(
                host=os.environ['DB_HOST'],
                user=os.environ['DB_USER'],
                passwd=os.environ['DB_PASS'],
                database=os.environ['DB_NAME']
            )

            logger.info('Connected to DB')

            return db
        except mysql.connector.errors.InterfaceError:
            if retry_count < 5:
                logger.warning(f'Unable to connect to DB. Sleeping for {SLEEP_AMOUNT} seconds and retrying.')

                sleep(SLEEP_AMOUNT)

                retry_count -= - 1
                logger.warning(f'Retrying attempt #{retry_count}')

                continue
            else:
                logger.error('Maximum number of retries reached.')
                raise


def get_db_connection():
    return db
