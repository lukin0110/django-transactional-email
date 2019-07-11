from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='transaction_email.index'),
    path('test', views.test_mail, name='transactional_email.test_mail')
]
