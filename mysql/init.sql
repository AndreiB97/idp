CREATE DATABASE db;

USE db;

CREATE TABLE QUESTION_POOL (
    QuestionID integer not null primary key auto_increment,
    Answer1 varchar(128) not null,
    Answer2 varchar(128) not null,
    Answer1_count integer default 0,
    Answer2_count integer default 0,
    Score integer default 0,
    Views integer default 0,
    Priority boolean default false
);

CREATE TABLE FLAGGED_OFFENSIVE_QUESTIONS (
    QuestionID integer not null primary key auto_increment,
    Answer1 varchar(128) not null,
    Answer2 varchar(128) not null
);

CREATE TABLE FLAGGED_LOW_SCORE_QUESTIONS (
    QuestionID integer not null primary key auto_increment,
    Answer1 varchar(128) not null,
    Answer2 varchar(128) not null,
    Answer1_count integer default 0,
    Answer2_count integer default 0,
    Score integer default 0,
    Views integer default 0
);

CREATE TABLE USER_SUBMITTED_QUESTIONS (
    QuestionID integer not null primary key auto_increment,
    Answer1 varchar(128) not null,
    Answer2 varchar(128) not null
);

INSERT INTO QUESTION_POOL(Answer1, Answer2, Views, Answer1_count, Answer2_count, Score)
VALUES
(
    "Lead a boring life from here forward",
    "Reborn with all your memories into a baby of the opposite sex.",
    1523221,
    251963,
    856620,
    1237297
),
(
    "Reach your ideal salary",
    "Reach your ideal weight",
    1447297,
    823446,
    365253,
    142971
),
(
    "Overdose on every drug at the same time",
    "Fall off a 100 story building",
    1255,
    604,
    622,
    148
),
(
    "Live in Antarctica for a year",
    "Live in Africa for a year",
    65,
    34,
    21,
    32
),
(
    "Be close with only one person, and only see them on Sundays",
    "Know many people and see them every day, but not be particularly close with any",
    1423,
    782,
    125,
    -124
),
(
    "Have the eyesight of an eagle",
    "Have the sense of smell of a dog",
    852,
    10,
    404,
    85
),
(
    "Take a sandwich tackle from 3 rugby players",
    "Jump off a two story roof",
    8520,
    1244,
    3887,
    1024
)
;

DELIMITER //

CREATE PROCEDURE add_question(IN ans1 varchar(128), IN ans2 varchar(128))
BEGIN
    INSERT INTO QUESTION_POOL(Answer1, Answer2)
    VALUES (ans1, ans2);
END //

CREATE PROCEDURE approve_question(IN id integer)
BEGIN
    DECLARE ans1 varchar(128);
    DECLARE ans2 varchar(128);

    SELECT Answer1, Answer2
    INTO ans1, ans2
    FROM USER_SUBMITTED_QUESTIONS
    WHERE QuestionID = id;

    DELETE FROM USER_SUBMITTED_QUESTIONS
    WHERE QuestionID = id;

    CALL add_question(ans1, ans2);
END //

CREATE PROCEDURE get_question()
BEGIN
    SELECT *
    FROM QUESTION_POOL
    ORDER BY RAND()
    LIMIT 1;
END //

CREATE PROCEDURE batch_get_questions(IN batch_size integer)
BEGIN
    SELECT *
    FROM QUESTION_POOL
    ORDER BY RAND()
    LIMIT batch_size;
END //

CREATE PROCEDURE add_user_submitted_question(IN ans1 varchar(128), IN ans2 varchar(128))
BEGIN
    INSERT INTO USER_SUBMITTED_QUESTIONS(Answer1, Answer2)
    VALUES (ans1, ans2);
END //

CREATE PROCEDURE increase_answer_count(IN id integer, IN answer_num integer)
BEGIN
    DECLARE old_count integer;

    IF answer_num = 1 THEN
        SELECT Answer1_count
        INTO old_count
        FROM QUESTION_POOL
        WHERE QuestionID = id;

        UPDATE QUESTION_POOL
        SET Answer1_count = old_count + 1
        WHERE  QuestionID = id;
    ELSEIF answer_num = 2 THEN
        SELECT Answer2_count
        INTO old_count
        FROM QUESTION_POOL
        WHERE QuestionID = id;

        UPDATE QUESTION_POOL
        SET Answer2_count = old_count + 1
        WHERE QuestionID = id;
    END IF;
END //

CREATE PROCEDURE increase_view_count(IN id integer)
BEGIN
    DECLARE old_count integer;

    SELECT Views
    INTO old_count
    FROM QUESTION_POOL
    WHERE QuestionID = id;

    UPDATE QUESTION_POOL
    SET Views = old_count + 1
    WHERE QuestionID = id;
END //

CREATE PROCEDURE score_question(IN id integer, IN new_score integer)
BEGIN
    DECLARE old_score integer;

    SELECT Score
    INTO old_score
    FROM QUESTION_POOL
    WHERE QuestionID = id;

    UPDATE QUESTION_POOL
    SET Score = old_score + new_score
    WHERE QuestionID = id;
END //

CREATE PROCEDURE get_user_submitted_questions()
BEGIN
    SELECT *
    FROM USER_SUBMITTED_QUESTIONS;
END //


CREATE PROCEDURE flag_user_submitted_question(IN id integer)
BEGIN
    DECLARE ans1 varchar(128);
    DECLARE ans2 varchar(128);

    SELECT Answer1, Answer2
    INTO ans1, ans2
    FROM USER_SUBMITTED_QUESTIONS
    WHERE QuestionID = id;

    DELETE FROM USER_SUBMITTED_QUESTIONS
    WHERE QuestionID = id;

    INSERT INTO FLAGGED_OFFENSIVE_QUESTIONS(Answer1, Answer2)
    VALUES (ans1, ans2);
END //

CREATE PROCEDURE get_question_pool()
BEGIN
    SELECT *
    FROM QUESTION_POOL;
END //

CREATE PROCEDURE flag_low_score_question(IN id integer)
BEGIN
    DECLARE ans1 varchar(128);
    DECLARE ans2 varchar(128);
    DECLARE ans1_count integer;
    DECLARE ans2_count integer;
    DECLARE old_views integer;
    DECLARE old_score integer;

    SELECT Answer1, Answer2, Answer1_count, Answer2_count, Views, Score
    INTO ans1, ans2, ans1_count, ans2_count, old_views, old_score
    FROM QUESTION_POOL
    WHERE QuestionID = id;

    DELETE FROM QUESTION_POOL
    WHERE QuestionID = id;

    INSERT INTO FLAGGED_LOW_SCORE_QUESTIONS(Answer1, Answer2, Answer1_count, Answer2_count, Views, Score)
    VALUES (ans1, ans2, ans1_count, ans2_count, old_views, old_score);
END //

CREATE PROCEDURE give_priority(IN id integer)
BEGIN
    UPDATE QUESTION_POOL
    SET Priority = true
    WHERE QuestionID = id;
END //

CREATE PROCEDURE remove_priority(IN id integer)
BEGIN
    UPDATE QUESTION_POOL
    SET Priority = false
    WHERE QuestionID = id;
END //

CREATE PROCEDURE get_priority_question()
BEGIN
    SELECT *
    FROM QUESTION_POOL
    WHERE Priority = true
    ORDER BY RAND()
    LIMIT 1;
END //

CREATE PROCEDURE get_flagged_offensive_questions()
BEGIN
    SELECT *
    FROM FLAGGED_OFFENSIVE_QUESTIONS;
END //

CREATE PROCEDURE delete_flagged_offensive_question(IN id integer)
BEGIN
    DELETE FROM FLAGGED_OFFENSIVE_QUESTIONS
    WHERE QuestionID = id;
END //

CREATE PROCEDURE restore_flagged_offensive_question(IN id integer)
BEGIN
    DECLARE ans1 varchar(128);
    DECLARE ans2 varchar(128);

    SELECT Answer1, Answer2
    INTO ans1, ans2
    FROM FLAGGED_OFFENSIVE_QUESTIONS
    WHERE QuestionID = id;

    CALL delete_flagged_offensive_question(id);

    INSERT INTO USER_SUBMITTED_QUESTIONS(Answer1, Answer2)
    VALUES (ans1, ans2);
END //

CREATE PROCEDURE delete_user_submitted_question(IN id integer)
BEGIN
    DELETE FROM USER_SUBMITTED_QUESTIONS
    WHERE QuestionID = id;
END //

CREATE PROCEDURE delete_question_from_pool(IN id integer)
BEGIN
    DELETE FROM QUESTION_POOL
    WHERE QuestionID = id;
END //

CREATE PROCEDURE get_flagged_low_score_questions()
BEGIN
    SELECT *
    FROM FLAGGED_LOW_SCORE_QUESTIONS;
END //

CREATE PROCEDURE delete_flagged_low_score_question(IN id integer)
BEGIN
    DELETE FROM FLAGGED_LOW_SCORE_QUESTIONS
    WHERE QuestionID = id;
END //


DELIMITER ;