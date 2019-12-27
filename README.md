# Compensation-System

In order to get the project up and running we need to install swi-prolog & django framework which uses Python3 along with some additional packages

## Requirements and Installation Guide

### Requirements
- Python 3.8
- SWI-Prolog 7.6.4
- Django 3.0
- PySwip


### Install SWI-PROLOG
- Install **SWI-PROLOG** version **7.6.4** you can find it here [SWI-Prolog downloads](https://www.swi-prolog.org/download/stable?show=all)


### Install Python3
- Install **Python3** version **3.8.0** you can find it here [Download Python \| Python.org](https://www.python.org/downloads/)
- Then make sure that the python package installer ``pip`` is installed 
- **macOS :** Open a new terminal window and run the following command ``pip3 -V`` 
- **Windows :** In the command line and run this command ``pip --version``

### Install Django Framework
- **macOS :** Open a new terminal window and run this command ``pip3 install django``
- **Windows :** In the command line and run this command ``pip install django``

### Install PySwip
- **macOS :** Open a new terminal window and run this command ``pip3 install pyswip`` followed by these commands
  - ``export PATH=$PATH:/Applications/SWI-Prolog.app/Contents/swipl/bin/x86_64-darwin15.6.0 ``
  - ``export DYLD_FALLBACK_LIBRARY_PATH=/Applications/SWI-Prolog.app/Contents/swipl/lib/x86_64-darwin15.6.0``
- **Windows :** In the command line and run this command ``pip install pyswip``

## Run the Project
Open a terminal window and navigate to the directory compensation_backend which includes the file ``manage.py``

### Migrate Database
In order to generate the sqlite database tables for the project
- **macOS** run the command ``python3 manage.py migrate`` 
- **Windows** run the command ``python manage.py migrate``

### Run the Server
Now it's time to run the project server
- **macOS** run the command ``python3 manage.py runserver``
- **Windows** run the command ``python manage.py runserver``

Now the project should be up and running so open the browser ``http://127.0.0.1:8000/login/``

For logging in as an admin use the following credentials 
- **Username :** Omar
- **Password :** password

For logging in as a StaffMember use the following credentials
- **Username :** Nada_Hamed
- **Password :** password_

or 

- **Username :** Haytham_Ismail
- **Password :** password_

Also in order to view the database and insert records in tables ``127.0.0.1:8000/admin/``
