from django.urls import path

from . import views

urlpatterns = [
     path('zielona_gora/', views.index,name='index'),
     path('current/<str:longitude_lattitude>/',views.long_latt,name='long_latt'),
     path('table/',views.table,name='table'),
     path('random/<int:count>/', views.random_long_latt, name='random_long_latt'),
     path('average/<str:voivo>/',views.average_temperature_voivo,name='average_temperature_voivo'),
]
