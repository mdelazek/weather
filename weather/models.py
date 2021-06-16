import csv
import datetime
import random
import requests
from bs4 import BeautifulSoup
from django.db import models
from django.utils import timezone
from django.conf import settings
# Create your models here.
class WeatherLocationManager(models.Manager):
	def random_locations(self,count):
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


class VoivodshipManager(models.Manager):

	def fill_voivodship(self):
		with open('weather/wojewodztwa.csv','r',encoding='utf-8') as csvfile:
			csvreader = csv.reader(csvfile,delimiter=';')
			for row in csvreader:
				voivo = Voivodship(voivo_name=row[1])
				voivo.save()


class DistrictManager(models.Manager):

	def fill_district(self):
		with open('weather/powiaty.csv','r',encoding='utf-8') as csvfile:
			for row in csv.reader(csvfile,delimiter=';'):
				voivo_id = int(int(row[1])/2)
				district = District(district_name=row[2],voivodship = Voivodship(id=voivo_id))
				district.save()


class LocationManager(models.Manager):

	def get_data_to_from_openweather(self,city,district):
		url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_KEY}'
		response = requests.get(url).json()
		if response['cod'] == '404':
			return 0
		temperature_kelvin = response['main']['temp']
		temperature_celsius = int(float(temperature_kelvin) - 273.15)
		if District.objects.filter(district_name = district).count() > 1:
			for dup in District.objects.filter(district_name = district):
				dup_id = dup.id
			District.objects.filter(id = dup_id).delete()
		location = Location(district = District.objects.get(district_name = district), location_name = city,datetime = datetime.datetime.now(datetime.timezone.utc),temperature=temperature_celsius)
		location.save()
		

class WeatherLocation(models.Model):
	access_datetime = models.DateTimeField(default=timezone.now)
	icon = models.CharField(max_length=20)
	location = models.CharField(max_length=50)
	temperature = models.IntegerField()
	city = models.CharField(max_length=20)
	color = models.CharField(max_length=20)

	objects = WeatherLocationManager()

class Voivodship(models.Model):
	voivo_name = models.CharField(max_length=20)

	objects = VoivodshipManager()

class District(models.Model):
	voivodship = models.ForeignKey(Voivodship, on_delete=models.CASCADE)
	district_name = models.CharField(max_length=30)

	objects = DistrictManager()

class Location(models.Model):
	district = models.ForeignKey(District, on_delete=models.CASCADE)
	location_name = models.CharField(max_length=50)
	datetime = models.DateTimeField(default=timezone.now)
	temperature = models.IntegerField()

	objects = LocationManager()
