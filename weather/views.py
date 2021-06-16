import csv
import datetime
import random
import requests
from bs4 import BeautifulSoup
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
def get_from_drops(*longitude_lattitude):

	if longitude_lattitude == ():
		soup = BeautifulSoup(requests.get('https://www.drops.live/zielona-g%C3%B3ra-zielona-g%C3%B3ra-poland/51.93548,15.50643').text,'lxml')
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
	else:

		soup = BeautifulSoup(requests.get('https://www.drops.live/'+ longitude_lattitude[0]).text,'lxml')
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

def long_latt(request,longitude_lattitude):

	current_date = datetime.datetime.now(datetime.timezone.utc)
	template = loader.get_template('weather/long_latt.html')
	last_access = WeatherLocation.objects.filter(location=longitude_lattitude).order_by('-access_datetime')
	is_in_db = last_access.exists() and (current_date - last_access[0].access_datetime).seconds <= 900
	if is_in_db:
		context = {'temperature': str(last_access[0].temperature) + degree_sign,
			   'city': last_access[0].city, 'icon': last_access[0].icon, 'color': last_access[0].color}
	else:
		context = get_from_drops(longitude_lattitude)
		db = WeatherLocation(access_datetime = datetime.datetime.now(), icon=context['icon'], location = longitude_lattitude, temperature = int(context['temperature'][:-1]), city = context['city'], color = context['color'])
		db.save()
	return  HttpResponse(template.render(context,request))

def table(request):
	
	template = loader.get_template('weather/table.html')
	objects_db = WeatherLocation.objects.all()
	context = {'list': objects_db}
	return  HttpResponse(template.render(context,request))

def get_data_to_all_locations():
	with open('weather/miastopow.csv','r',encoding='utf-8') as csvfile:
		for i in csv.reader(csvfile,delimiter=';'):
			Location.objects.get_data_to_from_openweather(i[0],i[1])
def get_data_to_any_location():
	pass

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
