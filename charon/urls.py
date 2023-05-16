from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('box', views.connect_box, name='connect_box'),
]
