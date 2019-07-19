# django-transactional-email

> Work in progress (WIP). It's not ready for production use. I'm still working on it, my current focus is to solve my own needs.

`transactional_email` is a Django app that manages templates and the configurations of *transactional emails*. 
A transactional email is a type of email that's triggered by a user action on a website or mobile app. Some common 
examples of transactional emails include password resets, shipping confirmations, invoices and receipts, account 
notifications, social media updates, and welcome emails. :fire: :fire:

This app is build on top of the standard [Django email functionality](https://docs.djangoproject.com/en/2.2/topics/email/) 
and allows you to store mail templates in the database. The Django templating engine is used to load, render and send
templated emails.

#### Table Of Contents

* [Why this exists](#why-this-exists)
* [How to use](#how-to-use)
* [Setup](#setup)


## Why this exists?

* avoid dependency and lock-in on 3th party Transactional email services. Eg: SendGrid, Mailgun, Mandrill, etc
* dynamic copy & content creation of mail templates
* separation of concerns. Disconnect copy/content from your codebase and development flow. No new deployment needed when marketing wants to update their fancy copy.

However, you can still use Transactional Email services as email backend to actually send your mails from Django. Cfr: 
[Anymail](https://github.com/anymail/django-anymail).


## How to use
The `transactional_email` only exposes 3 methods. You should only interface with these methods and try to stay away
from accessing the models and other functionality directly. 
* `issue`: render a transactional email and send it
* `render`: render a transactional email
* `send`: send an email

Issue a transactional email:
```python
from transactional_email import issue
issue('test.mail_config', 'jeffrey@dudeism.com', {'foo': 'bar'})
```

Render a message (it won't send it):
```python
from transactional_email import render
message = render('test.mail_config', 'jeffrey@dudeism.com', {'foo': 'bar'})
print(message)
```

Send an email:
```python
from transactional_email import render, send
message = render('test.mail_config', 'jeffrey@dudeism.com', {'foo': 'bar'})
send(message.subject, message.from_email, message.to_email, message.body)
```


## Setup

#### 1. Install python package
```bash
pip install git+git://github.com/lukin0110/django-transactional-email@master#egg=django-transactional-email
#pip install django-transactional-email
```
Note: package has not been uploaded to PyPi yet.

#### 2. Add the Django app
Add `transactional_email` to `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'transactional_email',
    ...
]
```

#### 3. Add the template loader
Add `transactional_email.loader.DatabaseLoader` to `TEMPLATES.OPTIONS.loaders` in `settings.py`:

It should look something like this:
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'transactional_email.loader.DatabaseLoader',
            ]
        },
    }
]
```

#### 4. Configure url patterns
Add `transactional_email.urls` to the url patterns in `urls.py`:
```python
urlpatterns = [
    ...
    path('transactional_email/', include('transactional_email.urls')),
    ...
]
```

## TODO
- add code example on how to use
- dump templates from db to disk
- push to pypi
