import mysql.connector
import os
import logging
from time import sleep
from flask import Flask, jsonify, request

app = Flask(__name__)

db = None
retry_count = 0


@app.route('/questions', methods=['GET'])
def get_question():
    response = {}
    cursor = db.cursor()

    cursor.callproc('get_question')

    for result in cursor.stored_results():
        for row in result.fetchall():
            response = {
                'id': row[0],
                'red': row[1],
                'blue': row[2],
                'red_stats': row[3],
                'blue_stats': row[4],
                'score': row[5]
            }

    return jsonify(response), 200


@app.route('/questions', methods=['PUT'])
def submit_question():
    args = request.args
    print(args)
    return jsonify({}), 200


@app.route('/answers', methods=['PUT'])
def submit_answer():
    args = request.args
    print(args)
    return jsonify({}), 200


def connect_to_db():
    global db, retry_count

    try:
        db = mysql.connector.connect(
            host=os.environ['DB_HOST'],
            user=os.environ['DB_USER'],
            passwd=os.environ['DB_PASS'],
            database=os.environ['DB_NAME']
        )
    except mysql.connector.errors.InterfaceError:
        if retry_count < 5:
            retry_count -=- 1
            logging.warning(f'Unable to connect to DB. Retry #{retry_count}.')
            sleep(1)
            connect_to_db()
        else:
            logging.error('Maximum number of retries reached.')
            raise

    logging.info('Connected to DB')


if __name__ == '__main__':
    connect_to_db()
    app.run(port=80, host='127.0.0.1', debug=True)
