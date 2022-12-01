# 15 minute walk city
#### Check if You live in urbanists dream!
#### Video Demo: <URL>

## Preface - What is 15 minutes city

15 minutes city - It's slogan to describe idea. Idea of city environment where all daily human needs can be fulfilled in small area - within 15 minutes of walk or ride a bike. So consequence is no need to use car in daily basis. Hectares of roads and parkings could be converted into parks, squares, cafes, courts et. cetera.

This way of thinking is promoted by many urbanists, for example [Carlos Moreno](https://www.ted.com/talks/carlos_moreno_the_15_minute_city>) and is realized in more and more of cities. Especially Netherlands and Denmark are famous of abandonment of car-scoped design.

To simplify, according to Carlo Moreno it is crucial to place living, working, commerce, healthcare, education and entertainment services in closest area. To promote city environment where this is possible.

## Program - what do

Based on [OpenStreetMaps](https://www.openstreetmap.org/copyright) data and user input, program gather locations of living, work, commerce, healthare, education, and leisure closer that 15 minutes walk to user home. Outpout is comment of results and map that show all of desired amenities.

## Program - how work

1. At first user is asked about adress of home and work in format: street, housenumber, city. Then input is geocoded using tool [geopy](https://geopy.readthedocs.io/en/stable/), and API [Nominatim](https://nominatim.org/).

    >Geocoding is a process of converting name of place into specific location on earth. The same process we see when we type adress on google maps search, and maps show us specific place.

    Format of input is checked by regular expression. \
    If program return nothing or appeared some kind of error - user is asked again for input.

2. Next using [osmnx](https://geoffboeing.com/publications/osmnx-complex-street-networks/) program generate graph of walkable routes in radius of 1200 metres of user home location.

    >Graph is kind of simplified map with two types of information:
    >* nodes - each have id and specific location defined by [geographic coordinates](https://en.wikipedia.org/wiki/Geographic_coordinate_system).
    >* routes - defined by lenght, and id of two nodes which each route connect. Every route connect only two nodes.

3. Next step is download of database of amenities in radius of 1200 metres again with use of osmnx. Program asks OpenStreetMaps database specified [tags](https://wiki.openstreetmap.org/wiki/Tags)

    ```
    tag = {
        "leisure":"park",
        "amenity":
        ["restaurant", "fast_food", "cafe", "bar", "pub",
        "school", "kindergarten", "library",
        "marketplace",
        "doctors", "clinic", "pharmacy", "hospital",
        "theatre", "cinema", "social_centre", "dentist", "hospital"],
        "shop": ["convenience","supermarket"]
        }
    ```

    and return database in form of [GeoDataFrame](https://geopandas.org/en/stable/getting_started/introduction.html). It's just two dimensional table including information of geometry (kind of excel sheet). Geometry is stored in form of Points or Polygons or Multipolygins (series of Polygons) mapped on earth. Each node of geometry is defined by [geographic coordinates](https://en.wikipedia.org/wiki/Geographic_coordinate_system).

4. From last step we get quite big database with lot of columns.
    ```
                            addr:city addr:housenumber addr:postcode  addr:street       amenity cuisine  ... natural source:name    landuse full_name                              ways          type
    element_type osmid                                                                                   ...
    node         1167418840   Wrocław               21        51-672  Partyzantów    restaurant   pizza  ...     NaN         NaN        NaN       NaN                               NaN           NaN
                1200203343   Wrocław              12b        51-672  Partyzantów  kindergarten     NaN  ...     NaN         NaN        NaN       NaN                               NaN           NaN
                1368322319       NaN              NaN           NaN          NaN      pharmacy     NaN  ...     NaN         NaN        NaN       NaN                               NaN           NaN
                1368323544       NaN              NaN           NaN          NaN      pharmacy     NaN  ...     NaN         NaN        NaN       NaN                               NaN           NaN
                1368333050       NaN              NaN           NaN          NaN      pharmacy     NaN  ...     NaN         NaN        NaN       NaN                               NaN           NaN
    ...                           ...              ...           ...          ...           ...     ...  ...     ...         ...        ...       ...                               ...           ...
    way          569021468        NaN              NaN           NaN          NaN        school     NaN  ...     NaN         NaN  education       NaN                               NaN           NaN
                932825618        NaN              NaN           NaN          NaN           NaN     NaN  ...     NaN         NaN        NaN       NaN                               NaN           NaN
                1037300779       NaN              NaN           NaN          NaN  kindergarten     NaN  ...     NaN         NaN  education       NaN                               NaN           NaN
                1037300780       NaN              NaN           NaN          NaN        school     NaN  ...     NaN         NaN  education       NaN                               NaN           NaN
    relation     12137435         NaN              NaN           NaN          NaN           NaN     NaN  ...     NaN         NaN        NaN       NaN  [383094830, 568782428, 31795985]  multipolygon

    [93 rows x 78 columns]
    ```

    Lets clean this up with help of tools included in [pandas](https://pandas.pydata.org/) and [geopandas](https://geopandas.org/en/stable/). Remove not necessary information, change name of columns, explode Multipolygons into Polygons and add column called amn_centr which store information of point used to calculate distance to amenities:

    ```
                                        name       street housenumber       amenity                                           geometry                  amn_centr
    0                      Casa Della Pizza  Partyzantów          21    restaurant                          POINT (17.09707 51.10915)  POINT (17.09707 51.10915)
    1           Punkt Przedszkolny Niziołki  Partyzantów         12b  kindergarten                          POINT (17.09360 51.10783)  POINT (17.09360 51.10783)
    2                   Pod Złotym Jeleniem          NaN         NaN      pharmacy                          POINT (17.09756 51.10926)  POINT (17.09756 51.10926)
    3                               Miętowa          NaN         NaN      pharmacy                          POINT (17.10005 51.10960)  POINT (17.10005 51.10960)
    4                           Pod Jaworem          NaN         NaN      pharmacy                          POINT (17.10279 51.10165)  POINT (17.10279 51.10165)
    ..                                  ...          ...         ...           ...                                                ...                        ...
    90  Punkt Przedszkolny Montessori House          NaN         NaN  kindergarten  POLYGON ((17.08698 51.10384, 17.08692 51.10363...  POINT (17.08723 51.10366)
    91    Zespół Szkolno-Przedszkolny Nr 22          NaN         NaN        school  POLYGON ((17.09254 51.10474, 17.09253 51.10482...  POINT (17.09355 51.10524)
    92                     Park Szczytnicki          NaN         NaN          park  POLYGON ((17.07838 51.11011, 17.08155 51.11106...  POINT (17.08129 51.10889)
    93                     Park Szczytnicki          NaN         NaN          park  POLYGON ((17.08018 51.11962, 17.08034 51.11959...  POINT (17.08236 51.11495)
    94                     Park Szczytnicki          NaN         NaN          park  POLYGON ((17.08465 51.10805, 17.08466 51.10812...  POINT (17.08738 51.10776)

    [95 rows x 6 columns]
    ```
5. To the above database program add row with information about work - input from user in first step. Now program have complete database to start calculating distances.

6. Program calculating a closest route from each of amenity in table above to user home location. Data is saved into new column. Records further than 1200 meters are dropped.

    Actually this is a clue of funcionalisty of this program.
    At first when I started working on this issue my aproach was:

    >generate graph -> generate isochrone map using approach from [osmnx documentation](https://github.com/gboeing/osmnx-examples/blob/main/notebooks/13-isolines-isochrones.ipynb) - > remove from database points that are outside the 1200 metres isochrone.

    When I start digging into method used in example I realized that script from above checking actually route to every single ending of graph: [sourcecode](https://networkx.org/documentation/stable/_modules/networkx/generators/ego.html#ego_graph). It take a lot of resources and time. After above scrip there still should be checked which amenity centerpoint is inside the isochrome. And at least: result could not be true.

    So I went into my current approach.
    Checking route between home and every amenity seems brute force - but actually take a lot less time, and in one operation for every amenity we have a final result.

7. At the end we have database of amenities closer than 15 minutes walk. Program just respond to question: Do You live in 15 minutes city?

    To quantity the result I need some kind of simplification. So I divided possible amenities into 6 categories grouped into dictionary:
    ```
    #Categorize amenities
    amn_dict = {
        'food and drinks' : ["restaurant", "fast_food", "cafe", "bar", "pub", "ice_cream"], # At least one
        'education' : ["school", "kindergarten", "library"], # At least school and kindergarten
        'leisure' : ["theatre", "cinema", "social_centre", "park"], # At least one
        'shop' : ["marketplace", "convenience", "supermarket"], #At least one
        'health' : ["hospital", "doctors", "clinic", "pharmacy", "dentist"], # At least doctor or clinic, dentist and pharmacy
        'work' : "workplace" # Must be included
        }
    ```
    So since at this point if program find all necessity services from table below in generated database, it said that You live in 15 minutes city. Else It told you how far are you from urbanists dream.
    Note that set of categories from above are used from scientific reason. You can live succefully without any of them. If You want - fork the project and change them to Your desire:

    First modifiy tags :
    https://github.com/code50/106762219/blob/f886f903a4d4d216a9f9391f9ee0037f6e5440cd/project/project.py#L44-L54

    Second divide them into categories:
    https://github.com/code50/106762219/blob/f886f903a4d4d216a9f9391f9ee0037f6e5440cd/project/project.py#L75-L83

    At the end modify the respond:
    https://github.com/code50/106762219/blob/f886f903a4d4d216a9f9391f9ee0037f6e5440cd/project/project.py#L229-L340

8. OK. Now best part. Generating the map. I've used build funcionality [folium](http://python-visualization.github.io/folium/) used in [geopandas](https://geopandas.org/en/stable/docs/user_guide/interactive_mapping.html) examples. To color markers I've just added colour column to dataFrame which is read by map "builder".

Voila!

## Credits
Geocoding by [geopy](https://geopy.readthedocs.io/en/stable/) using [Nominatim](https://nominatim.org/) API. Data acquired from [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), downloaded using [osmnx](https://geoffboeing.com/publications/osmnx-complex-street-networks/), analyzed by [networkx](https://networkx.org/), processed with [pandas](https://pandas.pydata.org/), and [geopandas](https://geopandas.org/en/stable/), with geometry transformation using [shapely](https://shapely.readthedocs.io/en/stable/), finally ploted using [folium](http://python-visualization.github.io/folium/) with beautiful [stamen toner](http://maps.stamen.com/toner/#12/37.7706/-122.3782) as background.

Thank for CS50 team - because of You all of above was possible.