import mysql.connector
import logging
import os
from time import sleep

db = None
retry_count = 0
logger = None
EXIT = 'EXIT'


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


def cli():
    commands = [EXIT]
    while True:
        print('Available commands are:')
        print('\n'.join(commands))
        line = input()
        if line.upper() == EXIT:
            break


if __name__ == '__main__':
    init_logger()
    connect_to_db()
    cli()
