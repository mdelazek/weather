from django.urls import path

from . import views

urlpatterns = [
     #path('zielona_gora/', views.index,name='index'),
     path('current/<str:location>/',views.get_for_location,name='get_for_location'),
     path('table/',views.table,name='table'),
     path('random/<int:count>/', views.random_long_latt, name='random_long_latt'),
     path('average/<str:voivo>/',views.average_temperature_voivo,name='average_temperature_voivo'),
     path('voivodships/',views.voivodships_and_average_temperature,name='voivodships_and_average_temperature'),
     path('districts/<str:voivo_name>/',views.districts_and_average_temperature,name='districts_and_average_temperature'),
     path('locations/<str:district_name>/',views.locations_and_average_temperature,name='locations_and_average_temperature'),

]
