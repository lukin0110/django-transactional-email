from django.urls import path
from . import views

urlpatterns = [
    path('', views.mail_configs, name='transactional_email.index'),
    path('templates', views.templates, name='transactional_email.templates'),
    path('logs', views.logs, name='transactional_email.logs'),

    # POST to send a test mail
    path(
        'api/emails/',
        views.EmailLogsView.as_view(),
        name='transactional_email.test_mail'
    ),
    # GET to view an email log
    path(
        'api/emails/<int:pk>/',
        views.EmailLogsView.as_view(),
        name='transactional_email.view'
    ),
    # DELETE a template
    path(
        'api/templates/<int:pk>/',
        views.TemplatesView.as_view(),
        name='transactional_email.delete'
    ),
    # POST duplicates a deplate version
    path(
        'api/versions/<int:pk>/',
        views.TemplateVersionsView.as_view(),
        name='transactional_email.version'
    )
]
