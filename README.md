# liquidator
To install first install postgresql on your POSIX system.

Select python 3.10

On gentoo for example:

$eselect python list

Available Python interpreters, in order of preference:

  [1]   python3.9
  
  [2]   python3.10
  
  [3]   python3.11 (fallback)
  
#eselect python set 2

Create a postgresql database, key in password and database name in app.py by editing the following line replacing databaseUser, password and databaseName

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://databaseUser:password@localhost:5432/databaseName"

Install dependencies

$pip install wheel Flask flask-sqlalchemy psycopg2 web3 nested-loopup

Then in the root of the project folder

$flask run

View the website on the development server at http://127.0.0.1:5000

Credit given for used code in the source files.
