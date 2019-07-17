from django.urls import path
from . import views

urlpatterns = [
    path('', views.mail_configs, name='transactional_email.index'),
    path('templates', views.templates, name='transactional_email.templates'),
    path('logs/', views.logs, name='transactional_email.logs'),
    path('logs/<int:pk>/', views.log, name='transactional_email.log'),
    path('version/<int:pk>/preview', views.preview, name='transactional_email.preview'),
    path('version/<int:pk>/edit', views.edit, name='transactional_email.edit'),

    # POST to send a test mail
    path(
        'v1/emails/',
        views.EmailLogsView.as_view(),
        name='transactional_email.emails.test_mail'
    ),
    # GET to view an email log
    path(
        'v1/emails/<int:pk>/',
        views.EmailLogsView.as_view(),
        name='transactional_email.emails.view'
    ),
    # DELETE a template
    path(
        'v1/templates/<int:pk>/',
        views.TemplatesView.as_view(),
        name='transactional_email.templates.delete'
    ),
    # POST duplicates a Template version
    path(
        'v1/versions/<int:pk>/',
        views.TemplateVersionsView.as_view(),
        name='transactional_email.versions.duplicate'
    ),
    path(
        'v1/versions/<int:pk>/preview',
        views.TemplateVersionPreviewView.as_view(),
        name='transactional_email.versions.preview'
    )
]
