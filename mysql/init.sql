CREATE DATABASE db;

USE db;

CREATE TABLE QUESTION_POOL (
    QuestionID integer not null primary key auto_increment,
    Answer1 varchar(128) not null,
    Answer2 varchar(128) not null,
    Answer1_count integer default 0,
    Answer2_count integer default 0,
    Score integer default 0,
    Views integer default 0
);

CREATE TABLE FLAGGED_OFFENSIVE_QUESTIONS (
    QuestionID integer not null primary key auto_increment,
    Answer1 varchar(128) not null,
    Answer2 varchar(128) not null,
    Answer1_count integer default 0,
    Answer2_count integer default 0,
    Score integer default 0,
    Views integer default 0
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

DELIMITER ;