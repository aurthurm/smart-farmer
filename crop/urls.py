from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name='home'),
    path('about', views.about,name='about'),
    path('prediction', views.prediction,name='prediction'),
    path('schemes', views.schemes,name='schemes'),
    #path('latestweather', views.latestweather,name='latestweather'),
    path('latestweather', views.latestweather,name='latestweather'),

    path('livefeedpage', views.livefeedpage,name='livefeedpage'),
    path('community', views.community,name='community'),
    path('contact', views.contact,name='contact'),
    path('calculate/', views.index1, name="calculate"),
]

