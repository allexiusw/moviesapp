# MoviesApp

RESTful API to manage a small movie rental

## Installation

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

Create the database:

    python src/manage.py migrate

Create a superuser

    python src/manage.py createsuperuser 

Run the development server

    python src/manage.py runserver

Happy Hacking!
