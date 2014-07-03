#from __future__ import print_function
from mpl_toolkits.basemap import Basemap
import os, sys
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime,timedelta
from collections import defaultdict
from matplotlib.patches import Polygon
import math

def make_movie_with_heatmap(demand_spots,stops_unique,time_discrete,coordinates_look_up,demand_colors,stops_unique_grid,coordinates_grid,movie_name):
	#parameters
	plot_threshold = 0.05
	metadata = dict(title='Actual demand', artist='I.Zliobaite', comment='22.5.2014')
	
	fps=5
	save_path='mov/'
	dpi=80


	if	not(os.path.isdir(save_path)): #check if directory exists and if not then make
		os.mkdir(save_path)

	max_spots = max([y for x in demand_spots for y in x])
	max_grid = max([y for x in demand_colors for y in x])

	x = []
	y = []
	for stop in stops_unique:
		x.append(coordinates_look_up[stop][0])
		y.append(coordinates_look_up[stop][1])
	x1 = []
	y1 = []
	x2 = []
	y2 = []
	for stop in stops_unique_grid:
		x1.append(coordinates_grid[stop][0])
		y1.append(coordinates_grid[stop][1])
		x2.append(coordinates_grid[stop][2])
		y2.append(coordinates_grid[stop][3])

	fig = plt.figure(figsize=(16,9),facecolor='k',edgecolor='k')
	ax = fig.add_subplot(111)

	writer = animation.FFMpegWriter(fps=fps, metadata=metadata,bitrate=20000)

	frame = 0
	#with writer.saving(fig,os.path.join(save_path,movie_name),dpi):
	with writer.saving(fig,movie_name,dpi):
		for sk in range(len(time_discrete)):
			
			ax.cla()
			demand_now = demand_spots[sk]
			demand_grid_now = demand_colors[sk]
			time_now =time_discrete [sk]

			plot_demand_spot_with_heatmap(demand_now,x,y,ax,time_now,demand_grid_now,x1,y1,x2,y2,max_spots,max_grid)

			#save map
			plt.savefig(os.path.join(save_path, 'frame%d.png'%frame), dpi=dpi,facecolor='w',edgecolor='k')

			writer.grab_frame()
			frame += 1

def plot_demand_spot_with_heatmap(vector_demand,x,y,ax,time_now,vector_demand_grid,x1,y1,x2,y2,max_spots,max_grid):
	#print vector_demand_grid
	map = plot_background(ax)
	#plot_heat_spot(map)
	plot_heat_spots_grid(map,vector_demand_grid,x1,y1,x2,y2,max_grid)
	plot_demand_all_spots(x,y,map,vector_demand,time_now,max_spots)

def plot_background(ax):
	hmin = 24.79
	vmin = 60.14
	vmax = 60.26
	hmax = 25.04
	map = Basemap(projection='merc',lon_0=(hmin+hmax)/2,lat_0=(vmin+vmax)/2,resolution='l',llcrnrlat=vmin, llcrnrlon=hmin, urcrnrlat=vmax, urcrnrlon=hmax,ax=ax)
	#http://render.openstreetmap.org/cgi-bin/export?bbox=24.79,60.14,25.04,60.26&scale=100000&format=png
	h0,v0 = map(hmin,vmin)
	h1,v1 = map(hmax,vmax)
	im = plt.imshow(plt.imread('map_helsinki_h.png'),extent=[h0,h1,v0,v1],alpha=0.4)
	return map

def	plot_heat_spots_grid(map,vector_demand_grid,x1,y1,x2,y2,max_grid):
	#print vector_demand_grid
	xx1,yy1=map(y1,x1)
	xx2,yy2=map(y2,x2)
	for sk in range(len(vector_demand_grid)):
		if vector_demand_grid[sk]>0:
			vd = vector_demand_grid[sk]*1.0/max_grid
			lats = [ x1[sk], x2[sk], x2[sk], x1[sk] ]
			lons = [ y1[sk], y1[sk], y2[sk], y2[sk] ]
			draw_screen_poly_heat(lats, lons, map,vd)

def plot_demand_all_spots(x,y,map,vector_demand,time_now,max_spots):
	#print vector_demand
	x1,y1=map(y,x) # transforms coordinates to the appropriate projection
	pp = 0
	for sk in range(len(vector_demand)):
		plt.annotate(time_now, xy=(0, 1), xycoords='axes fraction')
		if vector_demand[sk]>0:
			#ms = round(vector_demand[sk]*50.0/max_spots)
			ms = 15
			map.plot(x1[sk],y1[sk],color = '#303030',marker = '.',markersize = ms)
			pp += 1
	if pp==0: #to prevent from printing coordinates on the plot
		x1,y1=map(24.79,60.14)
		map.plot(x1,y1,'k.')

def draw_screen_poly(lats, lons, m):
	x, y = m( lons, lats )
	xy = zip(x,y)
	poly = Polygon( xy, facecolor='red', alpha=0.1,edgecolor = 'none' )
	plt.gca().add_patch(poly)

def draw_screen_poly_heat(lats, lons, m,heat):
	x, y = m( lons, lats )
	xy = zip(x,y)
	poly = Polygon( xy, facecolor='red', alpha=heat,edgecolor = 'none' )
	plt.gca().add_patch(poly)


def deg2num(lat_deg, lon_deg, zoom):
	lat_rad = math.radians(lat_deg)
	n = 2.0 ** zoom
	xtile = int((lon_deg + 180.0) / 360.0 * n)
	ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
	return (xtile, ytile)

def num2deg(xtile, ytile, zoom):
	n = 2.0 ** zoom
	lon_deg = xtile / n * 360.0 - 180.0
	lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
	lat_deg = math.degrees(lat_rad)
	return (lat_deg, lon_deg)
