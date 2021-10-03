# MoviesApp

[![Build Status](https://app.travis-ci.com/allexiusw/moviesapp.svg?token=wYaBCkxqpAXSKTHgNo9f&branch=development)](https://app.travis-ci.com/allexiusw/moviesapp)

RESTful API to manage a small movie rental

## For development environment

Clone the repository:

    git@github.com:allexiusw/moviesapp.git

Move to the repository folder:

    cd moviesapp/

Create the virtual environment:

    python3 -m venv ~/.moviesapp

Activate the virtual env:

    . ~/.moviesapp/bin/activate

Install the requirements:

    pip install -r requirements.txt

Create your user and database in Postgres:

    user=moviesapp_user
    password=DoNotUseInProd123
    database=moviesapp_db

Run migrations:

    python src/manage.py migrate

Create a superuser

    python src/manage.py createsuperuser 

Run the development server

    python src/manage.py runserver

Happy Hacking!
