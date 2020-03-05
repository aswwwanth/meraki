# Meraki

## Installation

This guide provides a walkthrough to getting started with Meraki on a local machine. Please keep in mind that the application is being written in Python *3*.

Set-up Virtual Environment in the prefered location. Please ensure you have the latest version of Python 3 installed.
~~~
python3 -m venv venv
~~~
Enter the virtual environment
~~~
. venv/bin/activate
~~~
Install the requirements
~~~
pip install -r requirements.txt
~~~

Flask-Migrate extension is currently in use in the application in order to track the changes made frequently to the database schema. This results in the need to manually migrating the database with each change.

If using a seperate database, please perform the following operations on first use to build the necessary database tables. Please DO NOT perform if using the existing clould instances.

~~~
flask db init
flask db migrate
flask db upgrade
~~~

For each change to the Database model, please enter the following commands to add the new changes and commit to the database. If using existing shared cloud database solutions, please ask the developer managing the migrations.

~~~
flask db migrate
flask db upgrade
~~~

## To run the app

Be inside the switch directory.
~~~
python meraki.py
~~~
