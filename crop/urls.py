from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name='home'),
    path('about', views.about,name='about'),
    path('prediction', views.prediction,name='prediction'),
    path('schemes', views.schemes,name='schemes'),
    path('latestweather', views.latestweather,name='latestweather'),
    path('contact', views.contact,name='contact'),
    path('calculate', views.calculate, name="calculate"),
    path('ask-guru', views.ask_guru, name="ask-guru"),
]

