from logging import INFO
from flask import Flask, jsonify, request
from random import random
from db_connection.connect_helper import connect_to_db, set_logger, SLEEP_AMOUNT
from time import sleep
from contextlib import closing
import mysql.connector.errors as errors

app = Flask(__name__)
db = None
retry_count = 0


@app.route('/questions', methods=['GET'])
def get_question():
    global retry_count

    # random number between 0 and 1
    chance = random()
    response = None

    with closing(db.cursor()) as cursor:
        while True:
            # 25% chance of getting priority questions
            try:
                if chance > 0.25:
                    cursor.callproc('get_question')
                else:
                    cursor.callproc('get_priority_question')

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

                # in case of no priority questions available
                if response is None:
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

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    app.logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -=- 1
                    app.logger.warn(f'Retrying attempt #{retry_count}')
                    continue
                else:
                    app.logger.error('Maximum number of retries reached.')

                    raise

    retry_count = 0
    db.commit()

    return jsonify(response), 200


@app.route('/questions', methods=['PUT'])
def submit_question():
    global retry_count
    args = request.args

    with closing(db.cursor()) as cursor:
        while True:
            try:
                cursor.callproc('add_user_submitted_question', [args['answer1'], args['answer2']])

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    app.logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} seconds and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -= - 1
                    app.logger.warn(f'Retrying attempt #{retry_count}')

                    continue
                else:
                    app.logger.error('Maximum number of retries reached.')

                    raise

    retry_count = 0
    db.commit()
    app.logger.info(f'Added user submitted question {args}')

    return jsonify({}), 200


@app.route('/answers', methods=['PUT'])
def submit_answer():
    global retry_count

    args = request.args
    app.logger.info(f'Received answer {args}')

    with closing(db.cursor()) as cursor:
        while True:
            try:
                if args['answer'] == 'red':
                    cursor.callproc('increase_answer_count', (args['id'], 1))
                elif args['answer'] == 'blue':
                    cursor.callproc('increase_answer_count', (args['id'], 2))

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    app.logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} seconds and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -= - 1
                    app.logger.warn(f'Retrying attempt #{retry_count}')

                    continue
                else:
                    app.logger.error('Maximum number of retries reached.')

                    raise

    db.commit()
    retry_count = 0

    return jsonify({}), 200


@app.route('/score', methods=['PUT'])
def score():
    global retry_count

    args = request.args
    question_score = 1

    # make sure score is always 1 or -1
    try:
        if int(args['score']) < 0:
            question_score = -1
    except ValueError:
        app.logger.error(f'Received invalid score {args["score"]}')

        return jsonify({}), 400

    app.logger.info(f'Received score {args}')

    with closing(db.cursor()) as cursor:
        while True:
            try:
                cursor.callproc('score_question', (args['id'], question_score))

                break
            except errors.ProgrammingError:
                if retry_count < 5:
                    app.logger.warn(f'Unable to call procedure. Sleeping for {SLEEP_AMOUNT} seconds and retrying.')

                    sleep(SLEEP_AMOUNT)

                    retry_count -= - 1
                    app.logger.warn(f'Retrying attempt #{retry_count}')

                    continue
                else:
                    app.logger.error('Maximum number of retries reached.')

                    raise

    retry_count = 0
    db.commit()

    return jsonify({}), 200


if __name__ == '__main__':
    app.logger.setLevel(INFO)
    set_logger(app.logger)
    db = connect_to_db()
    app.run(port=80, host='0.0.0.0')
