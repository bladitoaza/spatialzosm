# SpatialzOSM

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**SpatialzOSM** is a Python package to generate disaggregated home locations and points of interests in coordinates for agent- and activity-based models using OSMnx. You can download features (e.g., points of interests, street networks, and buildings) from OpenStreetMaps using OSMnx, and sample home locations over the street networks or within buildings. 

## Installation

1. Before installing SpatialzOSM, you need to install the [OSMnx](https://osmnx.readthedocs.io/en/stable/index.html) package.    
Follow the [Installation](https://osmnx.readthedocs.io/en/stable/installation.html) guide to install OSMnx. You can also run OSMnx directly from the official OSMnx [Docker](https://hub.docker.com/r/gboeing/osmnx) image.

2. Once the OSMnx package is installed, you can install SpatialzOSM directly from GitHub with pip:

    ```bash
    pip install git+https://github.com/bladitoaza/spatialzosm.git
    ```
## Usage

### Getting started

To use SpatialzOSM you import the package and create an `Osmpoi`object containing the area of interest.

```python
import spatialzosm as spo

dresden = spo.Osmpoi({
        "city": "Dresden",
        "country": "Germany"
    }) 
```
Then, you can use the class methods. For example we extract the points of interest of **Dresden**.
```python
dresden_pois = dresden.fetch_osm_points() 
```
### Data requirements
When generating home locations into coordinates across the area, spatialzOSM requires the geospatial data of the zone units for the area (e.g., districts, statistical areas, traffic analysis zones) and the population counts.  

When generating homes along street networks or within buildings, the road network and the building shapes can be extracted first from OSM. See the [**User-reference**](###User-reference)  or [**Examples**](###Examples) sections for more information.

### User reference

#### `fetch_osm_points()` fetches a raw dataset of points of interest from OpenStreetMap for a given place.   
- Parameters:       
    None

- Returns:    
    pandas.DataFrame containing the POIs with their coordinates.

    The dataframe is also saved in a file with extension **_raw.csv.** For example, for Dresden the file would be **Dresden_raw.csv**.
   
#### ``filter_osm_points(dataframe)`` filters and categorizes the points of interest of the extracted raw dataframe from OSM based on OSM tagging system.   

- Parameters:   
	<span style="color:chocolate">dataframe</span> (pandas.DataFrame or str): The dataframe containing the POI data or the path to the **csv** file.   
- Returns:   
    pandas.DataFrame containing the POIs with their coordinates. 

    The dataframe is also saved in a file with extension **_clean.csv.** For example, for Dresden the file would be **Dresden_clean.csv**.

#### ``fetch_osm_streets(save_file=True, format='csv')`` fetches the street network from OpenStreetMap for a given place.

- Parameters: 

	- <span style="color:chocolate">save_file</span> (bool, optional): Whether to save the fetched data to a file.    
    Defaults to True.

	- <span style="color:chocolate">format</span> (str, optional): The file format to save the data in. It can be 'csv' or 'gpkg'.   
     Defaults to 'csv'.

- Returns:

	geopandas.GeoDataFrame: The fetched street network data as a GeoDataFrame.
    
    The geodataframe is saved in a file with extension _streets.csv or _streets.gpkg. For example, for Dresden the file would be Dresden_streets.gpkg.

#### `fetch_osm_buildings(save_file=True, format='csv')` fetches OSM buildings for a specific place and saves them as a file.

- Parameters: 
	- <span style="color:chocolate">save_file</span> (bool, optional): Whether to save the fetched data to a file.     
    Defaults to True.

	- <span style="color:chocolate">format</span> (str, optional): The file format to save the data in. It can be 'csv' or 'gpkg'.  
    Defaults to 'csv'.

- Returns:
	
    geopandas.GeoDataFrame: The buildings as a GeoDataFrame.

    The geodataframe is saved in a file with extension _buildings.csv or _buildings.gpkg. For example, for Dresden the file would be Dresden_buildings.gpkg.

#### ``create_houses_areas(zus, crs='EPSG:4326', method='uniform',pop_size=10)`` creates houses by sampling points on the areas of the zone units.

- Parameters:
	- <span style="color:chocolate">zus</span> (str or GeoDataFrame): The ZUs dataset to sample points from.    
    It can be either a file path to a shapefile or a GeoDataFrame object.

	- <span style="color:chocolate">crs</span> (str, optional): The coordinate reference system of the zone units dataset.    
    Defaults to 'EPSG:4326'.

	- <span style="color:chocolate">method</span> (str, optional): The method used for sampling points.   
        - If `method=uniform`, the points are sampled uniformly across the areas.
        - If `method=normal`, the points are sampled around a center point, which is the centroid of the shapes' areas, using a normal distribution.    

        Defaults to 'uniform'.

	- <span style="color:chocolate">pop_size</span>	(int or pandas.DataFrame): The population size used for generating random points on buildings.    
    If int, the number of random points is constant for all the units.   
    If Dataframe, the number of random points is variable.   
    Default is 10.   

- Returns:
	
    A CSV file containing the coordinates of the generated houses saved to disk.


#### ``create_houses_streets(streets,pop_size=10, crs='EPSG:4326',index_col=None)`` creates coordinates of houses based on street network data.

- Parameters:
	- <span style="color:chocolate">streets</span> (str or geopandas.GeoDataFrame): The input data representing street network. It can be a path to a CSV file, a geopandas.GeoDataFrame object, or a MultiDigraph containing the line geometries of the streets.

	- <span style="color:chocolate">pop_size</span>	(int or pandas.DataFrame): The population size used for generating random points on streets. Default is 10.   
    If int, the number of random points is constant for all the units.   
    If Dataframe, the number of random points is variable.   

	- <span style="color:chocolate">crs</span> (str): The coordinate reference system (CRS) to use.     
    Default is 'EPSG:4326'.
    
	- <span style="color:chocolate">index_col</span> (str): The name of the index column in the population size data.    
    Default is None.

- Returns:
	
    A CSV file containing the coordinates of the generated houses saved to disk.

#### `create_houses_buildings(buildings,index_column,building_column=None, pop_size=10,crs='EPSG:4326')` creates coordinates of houses based on building data.

- Parameters: 
	- <span style="color:chocolate">buildings</span> (str or GeoDataFrame or MultiDigraph): The input data representing containing the building shapes. It can be a path to a CSV file, a geopandas.GeoDataFrame object, or a MultiDigraph containing the shapes of the buildings.    
	If str, it represents the path to a CSV file containing building data.   
	If GeoDataFrame, it represents a GeoPandas object containing building data.      
	If MultiDigraph, it represents a network MultiDigraph object containing building data.     

    - <span style="color:chocolate">index_column</span> (str): The name of the column in the building data that represents the index.

    - <span style="color:chocolate">building_column</span> (str, optional): The name of the column in the building data that represents the building type.    
        Default is None.

	- <span style="color:chocolate">pop_size</span>	(int or pandas.DataFrame): The population size used for generating random points on buildings.   
    If int, the number of random points is constant for all the units.   
    If Dataframe, the number of random points is variable.     
    Default is 10. 

    - <span style="color:chocolate">crs</span> (str): The coordinate reference system (CRS) to use.    
    Default is 'EPSG:4326'.

- Returns:
	
    A CSV file containing the coordinates of the generated houses saved to disk.

### Examples
You can try an [example](https://github.com/bladitoaza/spatialzOSM-examples) interactively in a Jupyter notebook. 

## Support

If you have any issue or if you want to contribute to SpatialzOSM, please open an issue or submit a pull request!

## License 
SpatialzOSM is open source and licensed under the MIT license.