# Would You Rather
## Description
“Would You Rather” is a game where you are presented with a question with two answers. Once you pick an answer, you will be able to see how many people picked that answer. You can navigate between previous questions or get new ones. You can also submit your own questions to the servers. All questions follow a very simple format, they start with “Would you rather” and then provide two different options. E.g. “Would you rather… go to Hogwarts or go to Mordor?”.
## Architecture
![design diagram](https://github.com/AndreiB97/idp/blob/master/design_diagram.png "Design Diagram")

The design is split into four main components: the client, which will run on the user’s device and the administrator, server and filter, which will run within separate Docker containers.
### Client
The client will have a simple GUI through which the user can see the questions, answer them and submit their own. The communication between the client and the server will be achieved through HTTP requests.
### Server
The server will run within a Docker container and will offer a REST API through which it can communicate with clients. The server will be able to connect to the MySQL Database and call functions and procedures in order to get questions and save user submitted questions.
### Filter
The filter will run within a Docker container and periodically scan the questions in the database for offensive words and flag those questions. All flagged questions get moved to a different table and will not be sent to the server. The filter can also flag questions with a low score and move them to a different table so they can be reviewed by the administrator.
### Administrator
The administrator will run within a Docker container and will have a simple CLI through which an administrator can:
*	Review questions flagged for offensive language by the filter
*	Review questions flagged for having a low score by the filter
*	Review questions submitted by the users
*	Review questions in the current question pool
*	Add, move or remove questions from the Database
