# 2014 07 02 I.Zliobaite
# visualization of events over time based on grid ("heatmaps")
# place a grid over the city, count events in each square

import data_processing
import plotting

#define parameters
param_grid_width = 1 #km
param_discretization_step = 30 #in minutes
param_map_alpha = 0.97 #fading factor for previous
param_hour_range = range(7,18) #first inclusive, last exclusive, maximum range
param_number_of_days = 3
param_file_name = 'events.csv'
param_movie_name = 'events_movie.mp4'

#create a dataset for demo
data_processing.create_data(param_file_name,param_number_of_days)
print('done creating demo data')

#prepare data
coordinates_look_up,stop_sequence,times_start_trip = data_processing.make_coordinate_dictionary(param_file_name)
times_start_trip,stop_sequence = data_processing.sort_by_time(times_start_trip,stop_sequence)
coordinates_grid, stops_grid = data_processing.coordinates_to_grid(coordinates_look_up,param_grid_width)
stop_sequence_grid = data_processing.convert_stop_sequence_grid(stop_sequence,stops_grid)
print('done coordinate extraction')

time_discrete,demand_true_discrete,stops_unique = data_processing.discretize_observations(times_start_trip,stop_sequence,param_discretization_step,param_hour_range)
demand_fading_discrete = data_processing.fade_for_video(demand_true_discrete,param_map_alpha)
time_discrete_grid,demand_true_discrete_grid,stops_unique_grid = data_processing.discretize_observations(times_start_trip,stop_sequence_grid,param_discretization_step,param_hour_range)
demand_fading_discrete_grid = data_processing.fade_for_video(demand_true_discrete_grid,param_map_alpha)
print('done discretization')

#make a movie
plotting.make_movie_with_heatmap(demand_true_discrete,stops_unique,time_discrete,coordinates_look_up,demand_fading_discrete_grid,stops_unique_grid,coordinates_grid,param_movie_name)
print('done movie')
