<p align="center">
    <img src="https://user-images.githubusercontent.com/5360835/65427083-1af35900-de01-11e9-86ef-59f1eee79a68.png" width="230" height="70" alt="Bothub" />
</p>

# Bothub

[![Build Status](https://travis-ci.org/Ilhasoft/bothub-engine.svg?branch=master)](https://travis-ci.org/Ilhasoft/bothub-engine)
[![Coverage Status](https://coveralls.io/repos/github/Ilhasoft/bothub-engine/badge.svg?branch=master)](https://coveralls.io/github/Ilhasoft/bothub-engine?branch=master)
[![Code Climate](https://codeclimate.com/github/Ilhasoft/bothub-engine/badges/gpa.svg)](https://codeclimate.com/github/Ilhasoft/bothub-engine)
[![Python Version](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/)
[![License GPL-3.0](https://img.shields.io/badge/license-%20GPL--3.0-yellow.svg)](https://github.com/Ilhasoft/bothub-engine/blob/master/LICENSE)

## Development

Use ```make``` commands to ```check_environment```, ```install_requirements```, ```lint```, ```test```, ```migrate```, ```start```, ```migrations``` and ```collectstatic```.

| Command | Description |
|--|--|
| make help | Show make commands help
| make check_environment | Check if all dependencies was installed
| make install_requirements | Install pip dependencies
| make lint | Show lint warnings and errors
| make test | Run unit tests and show coverage report
| make migrate | Update DB shema, apply migrations
| make start | Start development web server
| make migrations | Create DB migrations files
| make collectstatic | Collects the static files into ```STATIC_ROOT```


### Fill database using fake data

Run ```pipenv run python ./manage.py fill_db_using_fake_data``` to fill database using fake data. This can help you to test [Bothub Webapp](https://github.com/Ilhasoft/bothub-webapp).


### Update Repositories Tests

Run ```pipenv run python ./manage.py update_repository_tests``` update repositories to sort by total tests.


### Migrate all training for aws

Run ```pipenv run python ./manage.py transfer_train_aws``` Migrate all trainings to an aws bucket defined in project settings.


### Update Last Train for Version System

Run ```pipenv run python ./manage.py update_last_train```


### Update Train Column Rasa Update Version

Run ```pipenv run python ./manage.py update_train_rasa_version```


#### Fake users infos:

| nickname | email | password | is superuser |
|---|---|---|---|
| admin | admin@bothub.it | admin | yes |
| user | user@bothub.it | user | no |


## Production

Docker images available in [Bothub's Docker Hub repository](https://hub.docker.com/r/ilha/bothub/).


# Deployment


## Heroku
Host your own Bothub Engine with [One-Click Deploy] (https://heroku.com/deploy).

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)



## Environment Variables

You can set environment variables in your OS, write on ```.env``` file or pass via Docker config.

| Variable | Type | Default | Description |
|--|--|--|--|
| SECRET_KEY | ```string```|  ```None``` | A secret key for a particular Django installation. This is used to provide cryptographic signing, and should be set to a unique, unpredictable value.
| DEBUG | ```boolean``` | ```False``` | A boolean that turns on/off debug mode.
| BASE_URL | ```string``` | ```http://api.bothub.it``` | URL Base Bothub Engine Backend.
| ALLOWED_HOSTS | ```string``` | ```*``` | A list of strings representing the host/domain names that this Django site can serve.
| DEFAULT_DATABASE | ```string``` | ```sqlite:///db.sqlite3``` | Read [dj-database-url](https://github.com/kennethreitz/dj-database-url) to configure the database connection.
| LANGUAGE_CODE | ```string``` | ```en-us``` | A string representing the language code for this installation.This should be in standard [language ID format](https://docs.djangoproject.com/en/2.0/topics/i18n/#term-language-code).
| TIME_ZONE | ```string``` | ```UTC``` | A string representing the time zone for this installation. See the [list of time zones](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
| STATIC_URL | ```string``` | ```/static/``` | URL to use when referring to static files located in ```STATIC_ROOT```.
| EMAIL_HOST | ```string``` | ```None``` | The host to use for sending email. When setted to ```None``` or empty string, the ```EMAIL_BACKEND``` setting is setted to ```django.core.mail.backends.console.EmailBackend```
| EMAIL_PORT | ```int``` | ```25``` | Port to use for the SMTP server defined in ```EMAIL_HOST```.
| DEFAULT_FROM_EMAIL | ```string``` | ```webmaster@localhost``` | Default email address to use for various automated correspondence from the site manager(s).
| SERVER_EMAIL | ```string``` | ```root@localhost``` | The email address that error messages come from, such as those sent to ```ADMINS``` and ```MANAGERS```.
| EMAIL_HOST_USER | ```string``` | ```''``` | Username to use for the SMTP server defined in ```EMAIL_HOST```.
| EMAIL_HOST_PASSWORD | ```string``` | ```''``` | Password to use for the SMTP server defined in ```EMAIL_HOST```.
| EMAIL_USE_SSL | ```boolean``` | ```False``` | Whether to use an implicit TLS (secure) connection when talking to the SMTP server.
| EMAIL_USE_TLS | ```boolean``` | ```False``` | Whether to use a TLS (secure) connection when talking to the SMTP server.
| ADMINS | ```string``` | ```''``` | A list of all the people who get code error notifications. Follow the pattern: ```admin1@email.com\|Admin 1,admin2@email.com\|Admin 2```
| CSRF_COOKIE_DOMAIN | ```string``` | ```None``` | The domain to be used when setting the CSRF cookie.
| CSRF_COOKIE_SECURE | ```boolean``` | ```False``` | Whether to use a secure cookie for the CSRF cookie.
| BOTHUB_WEBAPP_BASE_URL | ```string``` | ```http://localhost:8080/``` | The bothub-webapp production application URL. Used to refer and redirect user correctly.
| SUPPORTED_LANGUAGES | ```string```| ```en|pt``` | Set supported languages. Separe languages using ```|```. You can set location follow the format: ```[LANGUAGE_CODE]:[LANGUAGE_LOCATION]```.
| BOTHUB_NLP_BASE_URL | ```string``` | ```http://localhost:2657/``` | The bothub-blp production application URL. Used to proxy requests.
| CHECK_ACCESSIBLE_API_URL | ```string``` | ```http://localhost/api/repositories/``` | URL used by ```bothub.health.check.check_accessible_api``` to make a HTTP request. The response status code must be 200.
| SEND_EMAILS | ```boolean``` | ```True``` | Send emails flag.
| BOTHUB_ENGINE_AWS_S3_BUCKET_NAME | ```string``` | ```None``` | 
| BOTHUB_ENGINE_AWS_ACCESS_KEY_ID | ```string``` | ```None``` | 
| BOTHUB_ENGINE_AWS_SECRET_ACCESS_KEY | ```string``` | ```None``` | 
| BOTHUB_ENGINE_AWS_REGION_NAME | ```string``` | ```None``` | 
| BOTHUB_ENGINE_AWS_SEND |  ```bool``` | ```False``` | 
| BOTHUB_BOT_EMAIL |  ```string``` | ```bot_repository@bothub.it``` | Email that the system will automatically create for existing repositories that the owner deleted the account
| BOTHUB_BOT_NAME |  ```string``` | ```Bot Repository``` | Name that the system will use to create the account
| BOTHUB_BOT_NICKNAME |  ```string``` | ```bot_repository``` | Nickname that the system will use to create the account
| BOTHUB_ENGINE_USE_SENTRY |  ```bool``` | ```False``` | Enable Support Sentry
| BOTHUB_ENGINE_SENTRY |  ```string``` | ```None``` | URL Sentry
| ENVIRONMENT |  ```string``` | ```production``` | 
