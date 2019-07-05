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


## TODO
- send test mail via Admin 
- use codemirror html editor for template editing
- push to pypi
- dump templates from db to disk
- explain usage in README
