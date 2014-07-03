import datetime
import random
import csv as csv

def create_data(file_name,number_of_days):
	lat,lon = read_coordinates('coordinates.csv')
	number_of_stops = len(lat)
	
	time_end = datetime.datetime.now()
	time_end = time_end.replace(hour=5,minute=0, second=0, microsecond=0)
	time_now = time_end - datetime.timedelta(days=number_of_days)

	time_change = 1 #in min
	probability_init = 0.005
	hour_correction = [0]*24
	hour_correction[5] = 0.3
	hour_correction[6] = 0.6
	hour_correction[7] = 1.0
	hour_correction[8] = 1.5
	hour_correction[9] = 0.8
	hour_correction[10] = 0.5
	hour_correction[11] = 0.8
	hour_correction[12] = 1.2
	hour_correction[13] = 1.0
	hour_correction[14] = 0.7
	hour_correction[15] = 0.6
	hour_correction[16] = 1.0
	hour_correction[17] = 1.5
	hour_correction[18] = 1.0
	hour_correction[19] = 0.8
	hour_correction[20] = 0.5
	hour_correction[21] = 0.3
	hour_correction[22] = 0.2

	demand_probability = [random.random()*probability_init for sk in range(number_of_stops)]

	data = []
	while time_now<=time_end:
		for sk in range(number_of_stops):
			if random.random()<demand_probability[sk]*hour_correction[time_now.hour]:
				data.append([time_now,lat[sk],lon[sk]])
		time_now = time_now + datetime.timedelta(minutes=time_change)
		#if (time_now.hour==23): #skip night
			#time_now += datetime.timedelta(hours=6)
	write_data('events.csv',['time','lat','lon'],data)
	return

def write_data(file_name,header,list_name):
	with open(file_name, "wb") as f:
		writer = csv.writer(f)
		writer.writerow(header)
		writer.writerows(list_name)
	return

def read_coordinates(file_name):
	csv_file_object = csv.reader(open(file_name, 'rU'),delimiter=',')
	header = csv_file_object.next()
	lat = []
	lon = []
	for row in csv_file_object:
		col = header.index("lat")
		lat.append(float(row[col]))
		col = header.index("lon")
		lon.append(float(row[col]))
	return lat,lon