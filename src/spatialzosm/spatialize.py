import osmnx as ox
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon, MultiPolygon

""" module: osmpois_generator """
class Osmpoi:
	save_raw=False  #Save the raw obtained POIs from OSM
	save_filtered=True #Save the filtered POIs from OSM
	file_export= 'POIs'  #Default name for the file

	def __init__(self,place_name,):
		self.place_name = place_name

	def fetch_osm_points(self):
		"""
		Fetches points of interest (POIs) from OpenStreetMap (OSM) for a given place.

		Returns:
			dfbuildings (pandas.DataFrame): DataFrame containing the POIs with their coordinates.

		Raises:
			Exception: If an error occurs while obtaining the POIs.

		"""
		tags = {'aeroway':'aerodrome',
				'aeroway':'hangar',
				'aeroway':'helipad',
				'aeroway':'heliport',
				'aeroway':'terminal',
				'amenity':True,
				'building': True,
				'craft':True,
				'cuisine':True,
				'healthcare':True,
				'historic':True,
				'landuse':True,
				'leisure':True,
				'natural': 'beach',
				'natural':'cave_entrance',
				'natural':'hill',				 
				'office':True,
				'public_transport':'platform',
				'public_transport':'station',
				'shop':True,
				'sport':True,
				'tourism':True,
				'addr:street':True,
				'addr:flats':True
				}
		print('Obtaining POIs from OSM for {}. It can take a few minutes...'.format(self.place_name))
		#Set timeout
		ox.settings.requests_timeout=2500
		try:
			# Get POIs from place
			buildings = ox.features_from_place(self.place_name, tags)
		except Exception as e:
			print("An error occurred while obtaining POIs: ", e)
			return		
		# Calculate centroid coordinates
		centroid_x = buildings['geometry'].map(lambda poi: poi.centroid.x)
		centroid_y = buildings['geometry'].map(lambda poi: poi.centroid.y)
		# Insert coordinates into buildings dataframe
		buildings.insert(0, "x", centroid_x)
		buildings.insert(0, "y", centroid_y)
		#Save file	
		if self.save_raw:
			buildings.to_csv(self.file_export+'_raw.csv',index=False)
			print('Raw OSM POIs obtained successfully. File saved as {}_raw.csv'.format(self.file_export))
		else:
			print('Raw OSM POIs obtained successfully without saving file')
		dfbuildings=pd.DataFrame(buildings)
		return dfbuildings

	def filter_osm_points(self,dataframe):
		"""
		Filters and categorizes points of interest (POIs) in the given dataframe based on OSM tagging system.

		Parameters:
			dataframe (pandas.DataFrame or str): The dataframe containing the POI data or the path to a CSV file.

		Returns:
			None

		Raises:
			None
		"""
		if type(dataframe) == str:
			df= self.__read_csv_from_string(dataframe)
		else:
			df = dataframe.reset_index(drop=True)
		df["group"] = ''
		print('Filtering, cleaning and rearranging POIs for {}.\n It can take a few minutes...'.format(self.place_name))

		#AERODROME from OSM tagging system
		if 'aeroway' in df.columns:
        	df.loc[(df['amenity'].isnull()) & (~df['aeroway'].isnull()), 'amenity'] = df['aeroway']
		df.loc[df['amenity'].isin(['aerodrome','hangar','heliport','terminal']),'group']='aeroway'		
		#SUSTENANCE amenities from OSM tagging system
		if 'cuisine' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['cuisine'].isnull()),'amenity']='restaurant'
		df.loc[df['amenity'].isin(['bar','biergarten','cafe','fast_food','food_court', 'ice_cream','pub','restaurant']),'group']='sustenance'
		#CRAFT
		if 'craft' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['craft'].isnull()),'amenity']=df['craft']
		df.loc[df['amenity'].isin(['agricultural_engines', 'atelier', 'bakery', 'basket_maker', 'beekeeper', 'blacksmith', 'boatbuilder', 'bookbinder', 'brewery', 'builder', 'cabinet_maker', 'candlemaker', 'car_painter','carpenter','carpet_layer','caterer','chimney_sweeper','cleaning', 'clockmaker','confectionery', 'cooper', 'dental_technician', 'distillery', 'door_construction', 'dressmaker', 'electronics_repair', 'embroiderer', 'electrician', 'engraver', 'fence_maker', 'floorer', 'fruit_press', 'gardener', 'glaziery', 'goldsmith', 'grinding_mill', 'handicraft', 'hvac', 'insulation', 'interior_decorator', 'interior_work', 'jeweller', 'joiner', 'key_cutter', 'locksmith', 'metal_construction', 'mint', 'musical_instrument', 'oil_mill', 'optician', 'organ_builder', 'painter', 'parquet_layer', 'paver','photographer', 'photographic_laboratory', 'piano_tuner', 'plasterer', 'plumber', 'pottery', 'printer', 'printmaker', 'rigger', 'roofer', 'saddler', 'sailmaker', 'sawmill', 'scaffolder', 'sculptor', 'shoemaker', 'signmaker', 'stand_builder', 'stonemason', 'stove_fitter', 'sun_protection','tailor', 'tiler', 'tinsmith', 'toolmaker', 'turner', 'upholsterer', 'watchmaker', 'water_well_drilling', 'window_construction', 'winery']), 'group']='craft'
		#EDUCATION amenities from OSM tagging system
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['school', 'college','kindergarten', 'university'])), 'amenity']= df['building']
		df.loc[df['amenity'].isin(['college', 'driving_school', 'kindergarten', 'language_school', 'library', 'toy_library', 'training', 'music_school', 'school', 'university']),'group']='education'			
		#TRANSPORTATION amenities from OSM tagging system
		if 'highway' in df.columns:
			df.drop(df[~df['highway'].isnull()].index, inplace=True)
		if 'public_transport' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['public_transport'].isnull()),'amenity']='bus_station'
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['train_station','transportation'])), 'amenity']='train_station'
		df.loc[df['amenity'].isin(['bicycle_parking', 'bicycle_repair_station', 'bicycle_rental', 'boat_rental', 'boat_sharing', 'bus_station', 'car_rental', 'car_sharing', 'car_wash', 'compressed_air', 'vehicle_inspection', 'charging_station', 'ferry_terminal', 'fuel', 'motorcycle_parking', 'parking', 'parking_entrance', 'taxi','train_station']),'group']='transportation'
		#ENTERTAINMENT ARTS AND CULTURE amenities from OSM tagging system
		df.loc[df['amenity'].isin(['arts_centre', 'brothel', 'casino', 'cinema', 'community_centre', 'conference_centre', 'events_venue','exhibition_centre', 'fountain', 'gambling', 'love_hotel','music_venue', 'nightclub', 'planetarium', 'public_bookcase', 'social_centre', 'stripclub', 'studio', 'swingerclub', 'theatre']),'group']='entertainment'		
		#FACILITIES amenities from OSM tagging system
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['toilets'])), 'amenity']=df['building']
		df.loc[df['amenity'].isin(['bbq', 'bench', 'dog_toilet', 'dressing_room', 'drinking_water', 'give_box', 'mailroom', 'parcel_locker', 'shelter', 'shower', 'telephone', 'toilets', 'water_point', 'watering_place']), 'group']='facilities'		
		#FINANCIAL amenities from OSM tagging system
		df.loc[df['amenity'].isin(['atm', 'bank', 'bureau_de_change']),'group']='financial'		
		#HEALTHCARE amenities from OSM tagging system
		if 'healthcare' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['healthcare'].isnull()),'amenity']='doctors'
		if 'social_facility' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['social_facility'].isnull()), 'amenity']='social_facility'
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['hospital'])),'amenity']=df['building']
		df.loc[df['amenity'].isin(['baby_hatch', 'clinic','dentist','doctors', 'hospital', 'nursing_home', 'pharmacy', 'social_facility', 'veterinary']), 'group']='healthcare'
		#HISTORIC
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['castle'])), 'amenity']=df['building']
		if 'historic' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['historic'].isnull()),'amenity']=df['historic']
		df.loc[df['amenity'].isin(['aircraft_wreck','archaeological_site', 'battlefield', 'building','bunker',  'creamery', 'farm', 'manor', 'monastery','ruins']), 'group']='historic'		
		#LEISURE
		if 'leisure' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['leisure'].isnull()), 'group']='leisure'
			df.loc[(df['amenity'].isnull()) & (~df['leisure'].isnull()),'amenity']=df['leisure']
		#OFFICE
		if 'office' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['office'].isnull()), 'group']='office'
			df.loc[(df['amenity'].isnull()) & (~df['office'].isnull()),'amenity']=df['office']
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['office'])),'amenity']='administrative'
		df.loc[df['amenity'].isin(['administrative']), 'group']='office'
		#OTHERS amenities from OSM tagging system
		if 'landuse' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['landuse'].isin(['cemetery'])), 'amenity']='grave_yard'
		df.loc[df['amenity'].isin(['animal_boarding', 'animal_breeding', 'animal_shelter', 'baking_oven', 'childcare', 'clock', 'crematorium', 'dive_centre', 'funeral_hall','grave_yard', 'hunting_stand', 'internet_cafe', 'kitchen', 'kneipp_water_cure', 'lounger', 'marketplace', 'monastery', 'photo_booth', 'place_of_mourning', 'public_bath', 'refugee_site', 'vending_machine']), 'group']='others'		
		#PUBLIC SERVICE amenities from OSM tagging system
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['fire_station','government','public'])), 'amenity']=df['building']
		df.loc[df['amenity'].isin(['courthouse', 'fire_station', 'government','police', 'post_box', 'post_depot', 'post_office','public', 'prison', 'ranger_station', 'townhall']),'group']='public_service'
		#RELIGIOUS
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['cathedral','chapel', 'church', 'kingdom_hall', 'monastery','mosque','presbytery','religious','shrine','synagogue','temple'])),'amenity']='place_of_worship'
		if 'landuse' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['landuse'].isin(['religious'])),'amenity']='place_of_worship'
		df.loc[df['amenity'].isin(['place_of_worship']), 'group']='religious'
		#SHOP
		if 'shop' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['shop'].isnull()), 'group']='shop'
			df.loc[(df['amenity'].isnull()) & (~df['shop'].isnull()),'amenity']=df['shop']
		#SPORT
		if 'building' in df.columns:		
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['grandstand', 'pavilion', 'riding_hall', 'sports_hall', 'sports_centre', 'stadium'])), 'group']='sport'
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['grandstand', 'pavilion', 'riding_hall', 'sports_hall', 'sports_centre', 'stadium'])), 'amenity']=df['building']
		if 'sport' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['sport'].isnull()), 'group']='sport'
			df.loc[(df['amenity'].isnull()) & (~df['sport'].isnull()),'amenity']=df['sport']
		#TOURISM
		if 'building' in df.columns:
		df.loc[(df['amenity'].isnull()) & (df['building'].isin(['hotel'])),'group']='tourism'
		df.loc[(df['amenity'].isnull()) & (df['building'].isin(['hotel'])),'amenity']=df['building']
		if 'tourism' in df.columns:
		df.loc[(df['amenity'].isnull()) & (~df['tourism'].isnull()),'amenity']=df['tourism']
		df.loc[(df['amenity'].isnull()) & (~df['tourism'].isnull()), 'group']='tourism'
		#WASTE MANAGEMENT amenities from OSM tagging system DROP
		df.loc[df['amenity'].isin(['sanitary_dump_station', 'recycling', 'waste_basket', 'waste_disposal', 'waste_transfer_station']), 'group']='waste_management'		
		#BUILDING- ACCOMODATION
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['residential'])),'amenity']='house'
			df.loc[(df['amenity'].isnull()) &(df['building'].isin(['apartments','barracks', 'bungalow', 'cabin','detached', 'dormitory', 'farm', 'ger', 'house','houseboat','semidetached_house', 'shed','static_caravan','stilt_house','terrace','tree_house'])), 'amenity']=df['building']
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['commercial','industrial','kiosk', 'retail', 'supermarket'])),'amenity']=df['building']
		df.loc[df['amenity'].isin(['apartments','barracks', 'bungalow', 'cabin','detached', 'dormitory', 'farm', 'ger', 'house','houseboat', 'residential','semidetached_house', 'shed','static_caravan','stilt_house','terrace','tree_house']), 'group']='accomodation'
		if 'landuse' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['landuse'].isin(['residential'])),'amenity']='house'
			df.loc[(df['amenity'].isnull()) & (df['landuse'].isin(['commercial','industrial', 'retail'])),'amenity']=df['landuse']
		#BUILDING-SHOP		
		df.loc[df['amenity'].isin(['commercial','industrial','kiosk', 'retail', 'supermarket']), 'group']='shop'
		#LANDUSE
		if 'landuse' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['landuse'].isin(['farmland', 'farmyard','forest','grass','greenhouse', 'greenhouse_horticulture' , 'orchard', 'plant_nuersey', 'recreation_ground'])),'amenity']=df['landuse']
		df.loc[df['amenity'].isin(['farmland', 'farmyard','forest','grass','greenhouse','greenhouse_horticulture' ,'orchard','plant_nuersey', 'recreation_ground']), 'group']='landuse'

		#BUILDING - HOUSE
		if 'addr:housenumber' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['addr:housenumber'].isnull()),'amenity']='house'
		if 'addr:housename' in df.columns:
			df.loc[(df['amenity'].isnull()) & (~df['addr:housename'].isnull()),'amenity']='house'
		if 'building' in df.columns:
			df.loc[(df['amenity'].isnull()) & (df['building'].isin(['yes'])), 'amenity']='house'
		df.loc[df['amenity'].isin(['house']), 'group']='accomodation'	
		#CLEANING OF UNDEFINED AMENITITES
		df.drop(df[df['group']==''].index, inplace=True)
		df=df.reset_index()		
		#Eliminating unnecessary columns
		df=df[['x', 'y', 'name', 'group','amenity']]  
		#Save file
		if self.save_filtered:
			df.to_csv(self.file_export+'_clean.csv',index=False)
			print('OSM POIs cleaned successfully. File saved as {}_clean.csv'.format(self.file_export))
		else:
			print('OSM POIs cleaned successfully. File not saved to disk')		
		return df
	
	def fetch_osm_streets(self, save_file=True, format='csv'):
		"""
		Fetches the street network from OpenStreetMap (OSM) for a given place.

		Args:
			save_file (bool, optional): Whether to save the fetched data to a file. Defaults to True.
			format (str, optional): The file format to save the data in. Can be 'csv' or 'gpkg'. Defaults to 'csv'.

		Returns:
			geopandas.GeoDataFrame: The fetched street network data as a GeoDataFrame.

		"""
		print('Obtaining street network from OSM for {}. It can take a few minutes...'.format(self.place_name))
		try:
			# Get streets from place
			streets = ox.graph_from_place(self.place_name, network_type='all', simplify=True, retain_all=False)
		except Exception as e:
			print("An error occurred while obtaining POIs: ", e)
			return

		street_gdf = ox.convert.graph_to_gdfs(streets, nodes=False, edges=True, node_geometry=False)
		# Eliminate unnecessary columns
		street_gdf.drop(street_gdf.iloc[:, list(range(4, 6)) + list(range(10, street_gdf.columns.size))], inplace=True, axis=1)
		# Save file
		if save_file:
			# Convert to and save as geopandas
			for i in street_gdf.columns:
				if i == 'geometry':
					continue
				street_gdf[i] = street_gdf[i].astype(str)
			if format == 'gpkg':
				street_gdf.to_file(self.file_export + '_streets.gpkg', driver='GPKG')
				print('OSM streets obtained successfully. File saved as {}_streets.gpkg'.format(self.file_export))
			else:
				street_gdf.to_csv(self.file_export + '_streets.csv')
				print('OSM streets obtained successfully. File saved as {}_streets.csv'.format(self.file_export))
		else:
			print('OSM streets obtained successfully. File not saved to disk')
		return street_gdf

	def fetch_osm_buildings(self, save_file=True, format='csv'):
		"""
		Fetches OSM buildings for a specific place and saves them as a file.

		Args:
			save_file (bool, optional): Indicates whether to save the file or not. Defaults to True.
			format (str, optional): The format in which to save the file. Defaults to 'csv'.

		Returns:
			geopandas.GeoDataFrame: The buildings as a GeoDataFrame.

		Raises:
			Exception: If an error occurs while obtaining the buildings.

		"""
		tags = {'building': True}
		print('Obtaining buildings from OSM for {}. It can take a few minutes...'.format(self.place_name))
		# Set timeout
		ox.settings.requests_timeout = 2500
		try:
			# Get POIs from place
			buildings = ox.features_from_place(self.place_name, tags)
		except Exception as e:
			print("An error occurred while obtaining POIs: ", e)
			return

		columns_to_keep = ['geometry', 'amenity', 'building', 'type']  # replace with your column names
		# select columns to keep from buildings GeoDataFrame
		print('Filtering, cleaning and rearranging buildings for {}.\n It can take a few minutes...'.format(self.place_name))
		buildings = buildings[columns_to_keep]
		buildings = buildings[buildings['geometry'].apply(lambda geom: isinstance(geom, (Polygon, MultiPolygon)))]

		if save_file:
			# Convert to and save as geopandas
			for i in buildings.columns:
				if i == 'geometry':
					continue
				buildings[i] = buildings[i].astype(str)
			if format == 'gpkg':
				buildings.to_file(self.file_export+'_buildings.gpkg', driver='GPKG')
				print('OSM buildings obtained successfully. File saved as {}_buildings.gpkg'.format(self.file_export))
			else:
				buildings.to_csv(self.file_export+'_buildings.csv')
				print('OSM buildings obtained successfully. File saved as {}_buildings.csv'.format(self.file_export))
		else:
			print('OSM buildings obtained successfully. File not saved to disk')
		
		return buildings

	def create_houses_streets(self,streets,pop_size=10, index_col=None,road_column=None, crs='EPSG:4326'):	
		"""
		Create coordinates of houses based on street network data.

		Parameters:
			streets (str or geopandas.GeoDataFrame): The input data representing street network. It can be a path to a CSV file, a geopandas.GeoDataFrame object, or a MultiDigraph containing the line geometries of the streets.
			pop_size (int): The population size used for generating random points on streets. Default is 10.
			crs (str): The coordinate reference system (CRS) to use. Default is 'EPSG:4326'.
			index_col (str): The name of the index column in the population size data. Default is None.

		Returns:
			A CSV file containing the coordinates of the generated houses.

		Raises:
			None
		"""
		#Reading based on type of file
		if isinstance(streets, str): #reading csv file from disk	
			gdf = gpd.read_file(streets)		
		elif isinstance(streets, gpd.GeoDataFrame): #reading a Geopandas obejct
			gdf=streets
		else:  #reading MultiDigraph directly
			gdf = ox.convert.graph_to_gdfs(streets,nodes=False,edges=True,node_geometry=True)		
		
		if index_col is None:
			index_col= pop_size.index.name
		if road_column is None:
			road_column='highway'
		#Cleaning of type of street clumn	
		gdf.reset_index(inplace=True)
		
		highway_clean = [num.replace('\'', '').replace('[','').replace(']','').replace(' ','').strip().split(',') for num in gdf['highway']]
		street_type =['residential','pedestrian','living_street','tertiary','secondary','primary','unclassified']	
		gdf['highway']=highway_clean
		for st_type in street_type:
			gdf['highway'] = gdf['highway'].apply(lambda x: [st_type] if st_type in x and st_type != x[0] else x)
		gdf['highway'] = gdf['highway'].apply(lambda x: x[0])
		gdf['highway'] = gdf['highway'].astype('category')
		condition = gdf["highway"].isin(street_type)
		gdf= gdf[condition]
		gdf['highway'] = gdf['highway'].cat.remove_unused_categories()
		pop_size.sort_index(inplace=True)
		pop_size=pop_size.fillna(0)
		gdk= gdf.groupby([index_col,'highway'])
		street_TAZ = pd.DataFrame(gdk.size(),columns=['n_streets'])
		idx = pd.IndexSlice
		generator = np.random.default_rng()
		#Random generation of points based on the 4 types of street that sum the total of points needed 
		print('Calculating random number of points per street type...')
		num_per_type = pd.DataFrame(generator.multinomial(pop_size, [.55,.18,.18,.03,.02,.02,.02]),columns = street_type, index= pop_size.index)				
		df_pool = street_TAZ.loc[idx[:, 'residential'], :].merge(num_per_type,
		left_on=index_col,right_on=index_col)
		street_TAZ.loc[idx[:, 'residential'], 'points'] = np.array(df_pool['residential'],int)
		street_TAZ.loc[idx[:, 'secondary'], 'points'] = np.array(df_pool['secondary'], int)
		street_TAZ.loc[idx[:, 'tertiary'], 'points'] = np.array(df_pool['tertiary'], int)
		street_TAZ.loc[idx[:, 'primary'], 'points'] = np.array(df_pool['primary'], int)
		street_TAZ.loc[idx[:, 'pedestrian'], 'points'] = np.array(df_pool['pedestrian'], int)
		street_TAZ.loc[idx[:, 'living_street'], 'points'] = np.array(df_pool['living_street'], int)
		street_TAZ.loc[idx[:, 'unclassified'], 'points'] = np.array(df_pool['unclassified'], int)
		street_TAZ['points'] = street_TAZ['points'].astype(int)
		print('Calculating number of points per street...')
		result_df = street_TAZ.reset_index().apply(
			lambda row: generator.multinomial(row['points'],[1/row['n_streets']]*row['n_streets']) if (row['n_streets'] > 0) else np.nan, axis=1
			)
		result_df.dropna(inplace=True)
		df_points_per_street = []
		for i in result_df:
			for j in range(i.size):
				df_points_per_street.append(i[j])
				
		gdf.sort_values([index_col,'highway'],inplace=True)
		#Sampling points using Geopandas
		print('Sampling points on streets...')
		sampled_houses = self.__spatial_distribution(gdf,size=df_points_per_street,method='uniform',crs=crs)		
		sampled_houses=  sampled_houses.explode(ignore_index=True)
		list_of_tuples = list(zip(sampled_houses.geometry.x, sampled_houses.geometry.y))
		df = pd.DataFrame(list_of_tuples, columns =['x','y'])
		df.to_csv('sampled_houses_'+'streets'+'.csv',index=False)
		print("Sampling completed. Coordinates saved to disk.")

	def create_houses_buildings(self,buildings,pop_size=10,index_column=None,building_column=None, crs='EPSG:4326'):
		"""
			Creates coordinates of houses based on building data.

			Parameters:
			- buildings: str or GeoDataFrame or MultiDigraph
				- If str, it represents the path to a CSV file containing building data.
				- If GeoDataFrame, it represents a GeoPandas object containing building data.
				- If MultiDigraph, it represents a networkx MultiDigraph object containing building data.
			- index_column: str
				- The name of the column in the building data that represents the index.
			- building_column: str, optional
				- The name of the column in the building data that represents the building type. Default is None.
			- pop_size: int, optional
				- The population size. Default is 10.
			- crs: str, optional
				- The coordinate reference system. Default is 'EPSG:4326'.

			Returns:
			A CSV file containing the coordinates of the generated houses saved to disk.
	"""

		if type(buildings) == str: #reading csv file from disk	
			gdf = gpd.read_file(buildings)
		elif isinstance(buildings, gpd.GeoDataFrame): #reading a Geopandas object
			gdf=buildings
		else:  #reading MultiDigraph directly
			gdf = ox.convert.graph_to_gdfs(buildings,nodes=False,edges=True,node_geometry=True)
		if index_column is None:			
			index_column= pop_size.index.name
		if building_column is None:
			building_column='building'
		gdf.reset_index(inplace=True)
		gdf[building_column]=gdf[building_column].astype('category')
		building_type = gdf[building_column].unique()
		gdf[building_column]=gdf[building_column].cat.remove_unused_categories() 
			
		pop_size = pop_size.loc[gdf[index_column].unique()]
		pop_size.sort_index(inplace=True)

		gdk= gdf.groupby(index_column)
		street_TAZ = pd.DataFrame(gdk.size(),columns=['n_buildings'])
		street_TAZ['pop_size']= pop_size
		street_TAZ['pop_size']=street_TAZ['pop_size'].fillna(0) #Check
		idx = pd.IndexSlice
		generator = np.random.default_rng()
		street_TAZ.reset_index(inplace=True)
		street_TAZ['pop_size']= street_TAZ['pop_size'].astype(int)
		print('Calculating number of points per building...')
		result_df = street_TAZ.apply(
			lambda row: (generator.multinomial(row['pop_size'], [1/int(row['n_buildings'])] * int(row['n_buildings'])) if int(row['n_buildings']) > 0 else np.nan), axis=1
		)
		result_df.dropna(inplace=True)
		df_points_buildings = []

		for i in result_df:
			for j in range(i.size):
				df_points_buildings.append(i[j])
		print('Sampling points on buildings...')
		gdf.sort_values([index_column,building_column],inplace=True)		
		sampled_houses = self.__spatial_distribution(gdf,size=df_points_buildings,method='uniform',crs=crs)		
		sampled_houses= sampled_houses.explode(ignore_index=True)
		list_of_tuples = list(zip(sampled_houses.geometry.x, sampled_houses.geometry.y))
		df = pd.DataFrame(list_of_tuples, columns =['x','y'])
		df.to_csv('sampled_houses_'+'buildings'+'.csv',index=False)
		print("Sampling completed. Coordinates saved to disk.")

	def create_houses_areas(self,zus, method='uniform',pop_size=10, crs='EPSG:4326'):
			"""
			Creates houses areas by sampling points on a given ZU (zone unit) dataset.

			Parameters:
			- zus (str or GeoDataFrame): The ZUs dataset to sample points from. It can be either a file path to a shapefile or a GeoDataFrame object.
			- crs (str, optional): The coordinate reference system of the ZUs dataset. Defaults to 'EPSG:4326'.
			- method (str, optional): The method used for sampling points. Defaults to 'uniform'.
			- pop_size (int, optional): The number of points to sample. Defaults to 10.

			Returns:
			A CSV file containing the coordinates of the generated houses saved to disk.

			"""
			
			if isinstance(zus, str):
				gdf = gpd.read_file(zus)
			elif isinstance(zus, gpd.GeoDataFrame): #reading a Geopandas obejct
				gdf=zus
			else:  #reading MultiDigraph directly
				gdf = ox.convert.graph_to_gdfs(zus,nodes=False,edges=True,node_geometry=True)	
			#Sampling points on TAZ with distribution 
			print('Sampling points on areas...')		
			sampled_houses = self.__spatial_distribution(gdf,size=pop_size,method=method,crs=crs)		
			sampled_houses=  sampled_houses.explode(ignore_index=True)
			list_of_tuples = list(zip(sampled_houses.geometry.x, sampled_houses.geometry.y))
			df = pd.DataFrame(list_of_tuples, columns =['x','y'])		
			df.to_csv('sampled_houses_area_'+method+'.csv',index=False)
			print("Sampling completed. Coordinates saved to disk for method {}".format(method))
				
	def __spatial_distribution(self,gdf, size=10, method="uniform", rng=None,crs='EPSG:4326', **kwargs):
			"""
			Apply spatial distribution to a GeoDataFrame.

			Parameters:
			-----------
			gdf : GeoDataFrame
				The GeoDataFrame to apply spatial distribution to.
			size : int or array-like, optional
				The size of the spatial distribution. If int, it represents the number of points to sample uniformly or normally. If array-like, it represents the size of each point to sample normally. Default is 10.
			method : str, optional
				The method of spatial distribution. Possible values are "uniform" and "normal". Default is "uniform".
			rng : numpy.random.Generator or None, optional
				The random number generator to use for sampling. If None, the default generator will be used. Default is None.
			crs : str, optional
				The coordinate reference system (CRS) of the resulting GeoSeries. Default is 'EPSG:4326'.
			**kwargs : dict, optional
				Additional keyword arguments to pass to the sampling method.

			Returns:
			--------
			GeoSeries
				The resulting GeoSeries after applying the spatial distribution.

			Raises:
			-------
			AttributeError
				If the specified method is not supported.

			"""
			
			from spatialzosm.utils._randist import normal 
			if type(size) is not int:
				if isinstance(size, np.ndarray):
					size[np.isnan(size)] = 0
				size = list(map(int, size))

			if method == "uniform":
				result= gdf.sample_points(method=method,size=size)	
				return result					
			elif method == "normal":	
				if pd.api.types.is_list_like(size):
					result = [normal(geom, s, rng) for geom, s in zip(gdf.geometry, size)]
				else:
					result = gdf.geometry.apply(normal, size=size, rng=rng)
				return gpd.GeoSeries(result, crs=gdf.crs, index=gdf.index)	
			else:
				raise AttributeError(
				f"This module has no sampling method {method}."
				)
		
	def __read_csv_from_string(self, file_path):
		try:
			df = pd.read_csv(file_path, low_memory=False)
			return df
		except Exception as e:
			print(f"An error occurred while reading the CSV file: {e}")
			return None

if __name__ == "__main__":
	print("Running module alone")
