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