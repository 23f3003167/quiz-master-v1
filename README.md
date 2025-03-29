# quiz-master-v1
Quiz master app that allows users to attempt quizzes on any subject on his/her interest and upgrade their knowledge on the chosen subject. This acts as an exam preparation site for multiple courses

## Description
Quiz Master is an interactive platform designed to facilitate learning through subject-wise quizzes. Users can attempt quizzes, track scores, and improve their knowledge. Admins can manage users, subjects, and quizzes efficiently.

## Features

**User Module** - Register, login and take quizzes. See scores and perfomance in each Quiz. Search subjects and quizzes.

**Admin Module** - Login, Manage subjects, chapters, quizzes and questions. See Registered Users and users performance. 

## Technologies Used 

 - _Backend:_ Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Login

 - _Frontend:_ HTML, CSS, Bootstrap

 - _Database:_ SQLite/PostgreSQL

 - _Charting:_ Chart.js (for visualizing quiz scores)

## Getting Started

### Set up the Database

`flask db init` 

`flask db migrate -m "Initial Migrations"`

`flask db upgrade`

These commands initializes the database and applies migrations.

### Run the Application

`python app.py` - This will initialise the flask app. Imports database models and sets home route to the login page. A New database file will be created with predefined Admin Credentials (if not already created). 

`flask run` - to start the development server as it automatically detects the Flask app. 

**(`set FLASK_ENV=development` / `set FLASK_DEBUG=1` - Any changes in the code reflects immediately)**

