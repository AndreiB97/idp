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
