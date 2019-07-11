# django-transactional-email

`transactional_email` is a Django app that manages templates and the configurations of *transactional emails*. 
A transactional email is a type of email that's triggered by a user action on a website or mobile app. Some common 
examples of transactional emails include password resets, shipping confirmations, invoices and receipts, account 
notifications, social media updates, and welcome emails.

This app is build on top of the standard [Django email functionality](https://docs.djangoproject.com/en/2.2/topics/email/) 
and allows you to store mail templates in the database. The Django templating engine is used to load and send
templated emails.

## Why this exists?

* avoid dependency and lock-in on 3th party Transactional email services. Eg: SendGrid, Mailgun, Mandrill, etc
* dynamic copy & content creation of mail templates
* separation of concerns. Copy/content changes don't need to be part of your codebase and development flow

However, you can still use Transactional Email services as email backend to actually send your mails from Django. Cfr: 
[Anymail](https://github.com/anymail/django-anymail).


## Setup

#### 1. Install python package
```bash
pip install django-transactional-email
```

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
Add `transactional_email.urls` to the url patters in `urls.py`:
```python
urlpatterns = [
    ...
    path('transactional_email/', include('transactional_email.urls')),
    ...
]
```


## TODO
- use codemirror html editor for template editing
- push to pypi
- dump templates from db to disk
