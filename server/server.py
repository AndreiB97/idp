import mysql.connector
import os
from logging import INFO
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
            app.logger.info(f'Sending question {row}')

            response = {
                'id': row[0],
                'red': row[1],
                'blue': row[2],
                'red_stats': row[3],
                'blue_stats': row[4],
                'score': row[5]
            }

    cursor.callproc('increase_view_count', (response['id'], ))

    db.commit()

    return jsonify(response), 200


@app.route('/questions', methods=['PUT'])
def submit_question():
    args = request.args
    cursor = db.cursor()

    cursor.callproc('add_user_submitted_question', [args['answer1'], args['answer2']])

    db.commit()
    app.logger.info(f'Added user submitted question {args["answer1"]}, {args["answer2"]}')

    return jsonify({}), 200


@app.route('/answers', methods=['PUT'])
def submit_answer():
    args = request.args

    app.logger.info(f'Received answer {args}')

    cursor = db.cursor()

    if args['answer'] == 'red':
        cursor.callproc('increase_answer_count', (args['id'], 1))
    elif args['answer'] == 'blue':
        cursor.callproc('increase_answer_count', (args['id'], 2))

    db.commit()

    return jsonify({}), 200


@app.route('/score', methods=['PUT'])
def score():
    args = request.args

    app.logger.info(f'Received score {args}')

    cursor = db.cursor()

    cursor.callproc('score_question', (args['id'], args['score']))

    db.commit()

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

        app.logger.info('Connected to DB')
    except mysql.connector.errors.InterfaceError:
        if retry_count < 5:
            retry_count -=- 1
            app.logger.warning(f'Unable to connect to DB. Retry #{retry_count}.')
            sleep(1)
            connect_to_db()
        else:
            app.logger.error('Maximum number of retries reached.')
            raise


if __name__ == '__main__':
    app.logger.setLevel(INFO)
    connect_to_db()
    app.run(port=80, host='0.0.0.0')
