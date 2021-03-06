import csv
import datetime
import random
import requests
from bs4 import BeautifulSoup
from django.db.models import Avg
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from weather.models import WeatherLocation, Voivodship, District, Location
def random_long_latt(request,count):
	i = 0
	while(i<count):
		latt = round(random.uniform(-90,90),6)
		long = round(random.uniform(-180,180),6)
		long_latt = str(latt) + ',' + str(long)
		soup = BeautifulSoup(requests.get('https://www.drops.live/' + long_latt).text,'lxml')
		test = soup.find('span',class_='temp temp left')
		if not test:
			continue
		temperature = soup.find('span',class_='temp temp left').text
		city = soup.find('span',class_='city').text
		icon = soup.find('img',class_='icon left')
		src ='https://www.drops.live' + icon['src']
		int_temp = int(temperature[:-1])
		if int_temp <= 10:
			color = "blue"
		elif int_temp < 30:
			color = "green"
		else:
			color = "red"
		db = WeatherLocation(access_datetime = datetime.datetime.now(), icon=src, location = long_latt, temperature = int_temp, city = city, color = color)
		db.save()
		i += 1
	return HttpResponse(request)		
degree_sign = u"\N{DEGREE SIGN}"
def get_from_drops(location):

	soup = BeautifulSoup(requests.get('https://www.drops.live/'+ location).text,'lxml')
	temperature = soup.find('span',class_='temp temp left').text
	city = soup.find('span',class_='city').text
	icon = soup.find('img',class_='icon left')
	int_temp = int(temperature[:-1])
	if int_temp <= 10:
		color = "blue"
	elif int_temp < 30:
		color = "green"
	else:
		color = "red"
	src ='https://www.drops.live' + icon['src']
	context = {'temperature':temperature,'city':city,'icon':src,'color':color}
	return context
"""
def index(request):
	
	current_date = datetime.datetime.now(datetime.timezone.utc)
	template = loader.get_template('weather/index.html')
	last_access = WeatherLocation.objects.filter(location='51.93548,15.50643').order_by('-access_datetime')
	is_in_db = last_access.exists() and (current_date - last_access[0].access_datetime).seconds <= 900
	
	if is_in_db:
		context = {'temperature': str(last_access[0].temperature) + degree_sign,
			   'city': last_access[0].city, 'icon': last_access[0].icon, 'color': last_access[0].color}
	else:
		context = get_from_drops()
		db = WeatherLocation(access_datetime = datetime.datetime.now(), icon=context['icon'], location = '51.93548,15.50643',temperature = int(context['temperature'][:-1]), city = context['city'], color = context['color'])
		db.save()
	return  HttpResponse(template.render(context,request))
"""
def get_for_location(request,location):

	current_date = datetime.datetime.now(datetime.timezone.utc)
	template = loader.get_template('weather/long_latt.html')
	last_access = WeatherLocation.objects.filter(city=location + ' Poland').order_by('-access_datetime')
	is_in_db = last_access.exists() and (current_date - last_access[0].access_datetime).seconds <= 900
	if is_in_db:
		context = {'temperature': str(last_access[0].temperature) + degree_sign,
			   'city': last_access[0].city, 'icon': last_access[0].icon, 'color': last_access[0].color}
	else:
		context = get_from_drops(location)
		db = WeatherLocation(access_datetime = datetime.datetime.now(), icon=context['icon'], location = location, temperature = int(context['temperature'][:-1]), city = context['city'], color = context['color'])
		db.save()
	return  HttpResponse(template.render(context,request))

def table(request):
	
	template = loader.get_template('weather/table.html')
	objects_db = WeatherLocation.objects.all()
	context = {'list': objects_db}
	return  HttpResponse(template.render(context,request))

def get_data_to_all_locations_when_new_db():
	with open('weather/miastopow.csv','r',encoding='utf-8') as csvfile:
		for i in csv.reader(csvfile,delimiter=';'):
			Location.objects.get_data_to_from_openweather(i[0],i[1])
	with open('weather/Brakujace_miasta.csv','r',encoding='utf-8') as csvfile:
		for miasto in csv.reader(csvfile,delimiter=';'):
			Location.objects.get_data_to_from_openweather(miasto[0],miasto[0])
def get_data_to_all_location():
	
	locations = Location.objects.all()
	name_list = []
	for location in locations:
		if location.location_name not in name_list:
			Location.objects.get_data_to_from_openweather(location.location_name,location.district.district_name)
			name_list.append(location.location_name)

def voivodships_and_average_temperature(request):
	
	fifteen_minutes = datetime.timedelta(minutes=15)
	voivodships = Voivodship.objects.all()
	average_temp = []
	for voivo in voivodships:
		last_access = Location.objects.filter(district__voivodship__voivo_name__startswith=voivo.voivo_name).order_by('-datetime')
		locations = Location.objects.filter(district__voivodship__voivo_name__startswith=voivo.voivo_name).filter(datetime__date__gte = last_access[0].datetime - fifteen_minutes).aggregate(Avg('temperature'))['temperature__avg']
		average_temp.append(round(locations,2))
	voi_and_temp = zip(voivodships, average_temp)
	context = {'voivodships': voivodships, 'voi_and_temp': voi_and_temp, 'last_survey': (last_access[0].datetime + datetime.timedelta(hours=2)).strftime("%B,%d,%Y %H:%M")}
	return HttpResponse(loader.get_template('weather/voivodships.html').render(context,request))

def districts_and_average_temperature(request,voivo_name):
	
	fifteen_minutes = datetime.timedelta(minutes=15)
	districts = District.objects.filter(voivodship__voivo_name__startswith = voivo_name)
	average_temp = []
	for district in districts:
		last_access = Location.objects.filter(district__district_name__startswith=district.district_name).order_by('-datetime')
		locations = Location.objects.filter(district__district_name__startswith=district.district_name).filter(datetime__date__gte = last_access[0].datetime - fifteen_minutes).aggregate(Avg('temperature'))['temperature__avg']
		average_temp.append(round(locations,2))
	district_and_temp = zip(districts, average_temp)
	context = {'districts': districts, 'district_and_temp':district_and_temp, 'last_survey': (last_access[0].datetime + datetime.timedelta(hours=2)).strftime("%B,%d,%Y %H:%M")}

	return HttpResponse(loader.get_template('weather/districts.html').render(context,request))

def locations_and_average_temperature(request,district_name):
	
	fifteen_minutes = datetime.timedelta(minutes=15)
	last_access = Location.objects.filter(district__district_name__startswith = district_name).order_by('-datetime')
	locations = Location.objects.filter(district__district_name__startswith = district_name).filter(datetime__date__gte = last_access[0].datetime - fifteen_minutes)
	context = {'locations': locations, 'last_survey': (last_access[0].datetime + datetime.timedelta(hours=2)).strftime("%B,%d,%Y %H:%M")}

	return HttpResponse(loader.get_template('weather/locations.html').render(context,request))


def average_temperature_voivo(request,voivo):
	
	while True:
		voivo = voivo.upper()
		current_datetime = datetime.datetime.now(datetime.timezone.utc)
		voivo_name = Location.objects.filter(district__voivodship__voivo_name__startswith=voivo)[0].district.voivodship.voivo_name
		last_access = Location.objects.filter(district__voivodship__voivo_name__startswith=voivo).order_by('-datetime')
		is_in_db = last_access.exists() and (current_datetime - last_access[0].datetime).seconds <= 900
		fifteen_minutes = datetime.timedelta(minutes=15)
		name_list = []
		if is_in_db:
	
			location_voivo_name = Location.objects.filter(district__voivodship__voivo_name__startswith=voivo).filter(datetime__date__gte=current_datetime - fifteen_minutes)
			count = 0
			sum_temp = 0
			for temp in location_voivo_name:
				if temp.location_name not in name_list:
					sum_temp += temp.temperature
					count += 1
					name_list.append(temp.location_name)
			average_temp = round(sum_temp/count,2)
			context = {'average': str(average_temp) + degree_sign, 'voi': location_voivo_name, 'voivo_name': voivo_name}
			break
		else:
			voivodship = Location.objects.filter(district__voivodship__voivo_name__startswith=voivo)
			for data in voivodship:
				if data.location_name not in name_list:
					Location.objects.get_data_to_from_openweather(data.location_name,data.district.district_name)
					name_list.append(data.location_name)
			name_list.clear()
	return HttpResponse(loader.get_template('weather/average.html').render(context,request))
