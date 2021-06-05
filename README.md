# The Unuseful API

I have used Python with Django to build an app which consumes the Random Useless Facts API http://randomuselessfact.appspot.com and Google Cloud Translation https://cloud.google.com/translate

## Installation

- Clone or download the repository
- No environment variables needed
- From the project root folder, enter the following commands into the terminal:

Install pipenv with pip:

    $ pip install pipenv

Navigate into the shell:

    $ pipenv shell

Install all packages from Pipfile:

    $ pipenv install

Run the server:

    $ python manage.py runserver

## Google Translation Authentication

I've used the Google Cloud Platform's Translation API for the translation of facts in Part Two. Users can be authenticated via the following method:

- I will grant your email address access to a Service Account called `cloud-translation-service` on my "Unuseful API" Google Cloud Project
- Navigate to the "Keys" tab. Click "Add Key" -> "Create new key" -> "JSON" -> "Create"
- This will download a JSON key file to your computer
- Move the JSON file into the project root folder and rename `unuseful-api.json`

You should now be able to access the Google Translation APIs via the `/facts/{factId}/lang={languageCode}` endpoint
