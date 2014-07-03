import datetime
import time
import random
import csv as csv
from collections import defaultdict
import numpy as np

def create_data(file_name,number_of_days):
	lat,lon = read_coordinates('coordinates.csv')
	number_of_stops = len(lat)
	
	time_end = datetime.datetime.now()
	time_end = time_end.replace(hour=5,minute=0, second=0, microsecond=0)
	time_now = time_end - datetime.timedelta(days=number_of_days)

	time_change = 1 #in min
	probability_init = 0.007
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
				data.append([time_now,lat[sk],lon[sk],sk])
		time_now = time_now + datetime.timedelta(minutes=time_change)
		#if (time_now.hour==23): #skip night
			#time_now += datetime.timedelta(hours=6)
	write_data(file_name,['time','lat','lon','id'],data)
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

def read_events(file_name):
	csv_file_object = csv.reader(open(file_name, 'rU'),delimiter=',')
	header = csv_file_object.next()
	times_start_trip = []
	lat = []
	lon = []
	id = []
	for row in csv_file_object:
		col = header.index("time")
		time_extracted = time.strptime(row[col], "%Y-%m-%d %H:%M:%S") #2014-06-28 06:57:00
		times_start_trip.append(datetime.datetime(*time_extracted[:6]))
		col = header.index("lat")
		lat.append(float(row[col]))
		col = header.index("lon")
		lon.append(float(row[col]))
		col = header.index("id")
		id.append(float(row[col]))
	return times_start_trip, lat, lon, id


def make_coordinate_dictionary(file_name):
	times_start_trip,lat,lon,stop_sequence = read_events(file_name)
	coordinates_look_up = defaultdict(list)
	for sk in range(len(stop_sequence)):
		if int(stop_sequence[sk]) not in coordinates_look_up:
			coordinates_look_up[int(stop_sequence[sk])].append(lat[sk])
			coordinates_look_up[int(stop_sequence[sk])].append(lon[sk])
	return coordinates_look_up,stop_sequence,times_start_trip

def coordinates_to_grid(coordinates,grid_width):
	const_lat_km = 111.0 #per 1 degree
	const_lon_km = 56.0 #per 1 degree
	const_new_idx = 1000
	latmax = max(coordinates.items(), key=lambda a: a[1][0])[1][0]
	lonmax = max(coordinates.items(), key=lambda a: a[1][1])[1][1]
	latmin = min(coordinates.items(), key=lambda a: a[1][0])[1][0]
	lonmin = min(coordinates.items(), key=lambda a: a[1][1])[1][1]
	latstep = grid_width/const_lat_km
	lonstep = grid_width/const_lon_km
	latstart = latmin - 50/const_lat_km + latstep#50m slack
	lonstart = lonmin - 50/const_lon_km + lonstep
	coordinates_grid = defaultdict(list)
	stops_grid = {}
	for stopID, coords in coordinates.items():
		latidx = 0
		lonidx = 0
		latbound = latstart
		lonbound = lonstart
		while coords[0] > latbound:
			latbound+= latstep
			latidx+=1
		while coords[1] > lonbound:
			lonbound+= lonstep
			lonidx+=1
		gridID = latidx*const_new_idx+lonidx
		stops_grid[stopID] = gridID
		if gridID not in coordinates_grid:
			coordinates_grid[gridID].append(latbound-latstep)
			coordinates_grid[gridID].append(lonbound-lonstep)
			coordinates_grid[gridID].append(latbound)
			coordinates_grid[gridID].append(lonbound)
	return coordinates_grid,stops_grid

def convert_stop_sequence_grid(stop_sequence,stops_grid):
	stop_sequence_grid = []
	for stop in stop_sequence:
		stop_sequence_grid.append(stops_grid[stop])
	return stop_sequence_grid

def discretize_observations(times_start_trip,stop_sequence,discretization_min,param_hour_range): #step in minutes
	demand = []
	times_demand = []
	stops_unique = list(set(stop_sequence))
	k = len(stops_unique)
	discretization_step = 60/discretization_min
	time_now = times_start_trip[0].replace(hour=param_hour_range[0], minute=0, second=0) + datetime.timedelta(minutes=discretization_min)
	time_end = times_start_trip[-1].replace(hour=param_hour_range[-1], minute=0, second=0)
	times_start_trip.append(time_end) #stopping criteria
	sk=0
	while time_now<=time_end:
		while times_start_trip[sk]<(time_now - datetime.timedelta(minutes=discretization_min)): #assume sorted times
			sk +=1 #fastforward irrelevant trips
		demand_vector_now = [0]*k #initialize demand in current slot
		while times_start_trip[sk]<time_now:
			idx = [ii for ii in range(len(stops_unique)) if stop_sequence[sk]==stops_unique[ii]]
			demand_vector_now[idx[0]] += 1
			sk += 1
		demand.append(demand_vector_now)
		times_demand.append(time_now)
		if (time_now.weekday()==4) and (time_now.hour==param_hour_range[-1]) and (time_now.minute==0): #if friday move to sunday
			time_now = time_now + datetime.timedelta(hours=48)
		if (time_now.hour==param_hour_range[-1]) and (time_now.minute==0): #if end of the day move to morning
			plus_hours = 24 - param_hour_range[-1] + param_hour_range[0]
			time_now = time_now + datetime.timedelta(hours=plus_hours)
		time_now = time_now + datetime.timedelta(minutes=discretization_min)
	times_start_trip = times_start_trip[0:-1] #remove stopping criterion, not needed anymore
	return times_demand,demand,stops_unique

def fade_for_video(demand,alpha):
	demand_faded = []
	vector_before = [0]*len(demand[0])
	for vector in demand:
		vector_now = []
		for i in range(len(vector)):
			v = vector[i] + alpha*vector_before[i]
			if v < 0.01:
				v = 0
			vector_now.append(v)
		demand_faded.append(vector_now)
		vector_before = vector_now
	return demand_faded

def sort_by_time(time_data,stop_sequence):
	time_data = np.array(time_data)
	ind_sorted = np.argsort(time_data)
	time_data = time_data[ind_sorted]
	stop_sequence = np.array(stop_sequence)[ind_sorted]
	time_data = list(time_data)
	stop_sequence = list(stop_sequence)
	return time_data,stop_sequence
