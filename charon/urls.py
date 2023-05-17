from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('box', views.connect_box, name='connect_box'),
    path('box/callback', views.callback_box, name='callback_box'),
    path('get_credentials', views.get_credentials, name='get_credentials'),
]
