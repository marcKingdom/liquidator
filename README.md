# liquidator
tested on python 3.10
To install first install postgresql on your POSIX system.
Install dependencies

$pip install wheel Flask flask-sqlalchemy psycopg2 web3 nested-loopup
Create a postgresql database, key in password and database name in app.py by editing the following line replacing databaseUser, password and databaseName

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://databaseUser:password@localhost:5432/databaseName"

Then in the root of the project folder

$flask run

View the website on the development server at http://127.0.0.1:5000

Credit given for used code in the source files.
