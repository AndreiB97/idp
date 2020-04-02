from logging import INFO
from flask import Flask, jsonify, request
from random import random
from db_connection.connect_helper import connect_to_db, set_logger

app = Flask(__name__)
db = None

# TODO catch procedure exception


@app.route('/questions', methods=['GET'])
def get_question():
    cursor = db.cursor()
    chance = random()

    response = None

    # 25% chance of getting priority questions
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

    db.commit()

    return jsonify(response), 200


@app.route('/questions', methods=['PUT'])
def submit_question():
    args = request.args
    cursor = db.cursor()

    cursor.callproc('add_user_submitted_question', [args['answer1'], args['answer2']])

    db.commit()

    app.logger.info(f'Added user submitted question {args}')

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
    question_score = 1

    # make sure score is always 1 or -1
    if args['score'] < 0:
        question_score = -1

    app.logger.info(f'Received score {args}')

    cursor = db.cursor()

    cursor.callproc('score_question', (args['id'], question_score))

    db.commit()

    return jsonify({}), 200


if __name__ == '__main__':
    app.logger.setLevel(INFO)
    set_logger(app.logger)
    db = connect_to_db()
    app.run(port=80, host='0.0.0.0')
