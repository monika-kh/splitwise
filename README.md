# splitwise
## Description
The project is a Python-based tool designed to track split balance of any expense made between a group of users.
# Backend setup
## Install virtualenv
pip install virtualenv then create env
```virtualenv -p python env```
## Activate the virtual environment
## On Windows:
venv\Scripts\activate
## On macOS and Linux:
source venv/bin/activate
## Install  requirements.txt
```pip install -r requirenents.txt```
## Setup Celery
You need to set up rabbitmq and redis to your system to run the celery worker in the backend for sending emails. 
## Run project
```python manage.py runserver```
