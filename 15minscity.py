import re
import sys
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx
import numpy as np
from IPython.display import IFrame
import folium
import geopandas as gpd
import pandas as pd
import inflect

p = inflect.engine()

# Globals
distance = 1200 # 15 mins. walk distance

def main():
    # User: Write location
    print("\nWelcome in 15 minutes city checker. \n\nThis program will figure out If You live in place located within 15 minutes walk to basic human services.\nPlease make shure that You have internet connection on.\n")
    #Get location
    while True:
        try:
            loc = get_location(input("Write Your home adress (Format: street, housenumber, city): "))
            break
        except (ValueError, Exception):
            print("Hey! Something went wrong. Please write again carefully. Maybe You ommit comma?")
            pass

    while True:
        try:
            waddr = input("Write Your work adress (Format: street, housenumber, city): ")
            workloc = get_location(waddr)
            print("\nThis will take few seconds...")
            break
        except (ValueError, Exception):
            print("Hey! Something went wrong. Please write again carefully. Maybe You ommit comma?")
            pass

    #Get map
    graph = get_graph(loc)

    #Define searched amenities
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

    #Download dataFrame with amenities
    df_amn = get_amenities(loc, tag)

    #Format dataframe
    df_amn = order(df_amn)

    #Adjust geometry
    df_amn = gmtr(df_amn)

    #Convert work location to dataframe
    work_df = get_workdf(waddr, workloc)

    #Connect work df with df_amn
    df_amn = pd.concat([df_amn, work_df], axis = 0)

    #Chose only amenities closer than 15mins walk
    df_amn = walkable(df_amn, loc, graph)

    #Categorize amenities
    amn_dict = {
        'food and drinks' : ["restaurant", "fast_food", "cafe", "bar", "pub", "ice_cream"], # At least one
        'education' : ["school", "kindergarten", "library"], # At least school and kindergarten
        'leisure' : ["theatre", "cinema", "social_centre", "park"], # At least one
        'shop' : ["marketplace", "convenience", "supermarket"], #At least one
        'health' : ["hospital", "doctors", "clinic", "pharmacy", "dentist"], # At least doctor or clinic and pharmacy
        'work' : "workplace"
        }

    #Comment data
    print("\n")
    print("Results: \n")
    print(comment(df_amn, amn_dict))

    #Add colours column
    df_amn["kolor"] = df_amn.apply(lambda x: get_kolor(x, amn_dict), axis=1)

    #Plot final
    plot(loc, df_amn)

    print("\nThis program generate map. Just download and open file called ./map.html and enjoy map of Your closest amenities.")

# Get location
def get_location(adress):
    if not re.search(r"^.+,.+,.+$", adress):
        raise ValueError
    if adress == "":
        raise ValueError

    geo = Nominatim(user_agent="15minscity/0.1")
    x = geo.geocode(adress, exactly_one=True)

    if x == None:
        raise ValueError
    else:
        return (x.latitude, x.longitude)

# Download street network
def get_graph(loc):
    global distance

    G = ox.graph.graph_from_point(loc, distance, network_type = "walk")
    return G

# Gather ameniities in area
def get_amenities(loc, tag):
    global distance

    #Download dataFrame
    df = ox.geometries_from_point(loc, tag, distance)
    df.index
    if df.empty:
        print("Looks like You're living outside the city. Or in the desert...")
        sys.exit()

    return df

# Format dataframe
def order(df):
    # Fixing colum name issue
    df = df.rename(columns ={'addr:street':'street', 'addr:housenumber':'housenumber'})

    #Remove unnecessary keys
    amn_list = ['amenity', 'leisure', 'shop']

    col = df.columns.tolist()

    amn_col = []
    for amn in amn_list:
        if amn in col:
            amn_col.append(amn)
    amn_basic = ['geometry', 'name', 'street', 'housenumber']
    amn_col = amn_basic + amn_col
    df = df[amn_col]

    #Merge amenity, shop and leisure
    df['amenit'] = np.nan

    for amn in amn_list:
        if amn in col:
            df['amenit'] = df.amenit.combine_first(df[amn])
            df = df.drop(columns=[amn])

    # Fixing colum name issue
    df = df.rename(columns ={'amenit':'amenity'})

    return df

#Adjust geometry
def gmtr(df):
    #Explode Multipolygons into polygons
    df = df.explode('geometry', ignore_index=True)

    print("Don't worry about warning below. I'm to lazy to turn that off. It doesn't matter")
    #Add reference coords
    df["amn_centr"] = df.centroid

    return df

#Convert work location to dataframe
def get_workdf(waddr, workloc):
    adress = waddr.split(",")

    stre = adress[0].removeprefix(" ").removesuffix(" ")
    housenum = adress[1].removeprefix(" ").removesuffix(" ")

    lat = float(workloc[0])
    lon = float(workloc[1])

    work_df = pd.DataFrame(
        {"name" : "Your workplace", "amenity" : "workplace", "street" : stre, "housenumber" : housenum, "Lat" : lat, "Lon" : lon}, index=[0]
    )

    work_df = gpd.GeoDataFrame(work_df, geometry=gpd.points_from_xy(work_df.Lon, work_df.Lat))

    work_df["amn_centr"] = work_df["geometry"]

    work_df = work_df[["name", "street", "housenumber", "amenity", "geometry", "amn_centr"]]

    return work_df

#Chose only amenities closer than 15mins walk
def walkable(df, loc, graph):

    # Get nearest starting point
    lat_st = float(loc[0])
    long_st = float(loc[1])
    start_n = ox.nearest_nodes(graph, long_st, lat_st)

    #Get shortest paths
    df['shortest'] = df.apply(lambda x: path_lenght(start_n, x, graph), axis=1)

    # Take path only below designed distance
    df = df.loc[lambda amenity: amenity['shortest'] <= distance, :]
    df = df.reset_index(drop=True)

    return df


#Calculate shortest path
def path_lenght(start_n, z, graph):
    global distance

    lat_sp = float(z.amn_centr.y)
    long_sp = float(z.amn_centr.x)

    stop_n = ox.nearest_nodes(graph, long_sp, lat_sp)

    route = ox.shortest_path(graph, start_n, stop_n, weight = "length")
    # Count paths lenght
    path_len = nx.path_weight(graph, route, weight = "length")

    return path_len

#Comment results
def comment(df_amn, amn_dict):

    amn_list = df_amn['amenity'].tolist()

    # Remove duplictes of amenities in dictionary
    amn_dict2 = {}
    for key in amn_dict:
        xlist = []
        for x in amn_dict[key]:
            if x in amn_list:
                xlist.append(x)
        amn_dict2[key] = xlist

    # Count amenities necessity for centrain level of live

    # Work
    if len(amn_dict2["work"]) > 0:
        wok = 1
        work_com = "You work nearly where You live. Enjoy daily walks!\n"
    else:
        wok = 0
        work_com = "Every day You lost Your precious time in daily commute\n"

    # Food and drinks
    if len(amn_dict2['food and drinks']) > 0:
        food = 1
        food_com = f"If You wanna go outside to eat something, or meet with friends there is {p.join(amn_dict2['food and drinks']).replace('_',' ')} near by.\n"
    else:
        food = 0
        food_com = "Unfortunately there's no close place to eat or drink. Forget to drink with friends and gently late walks to home.\n"

    # Education
    if set(["school", "kindergarten"]) <= set(amn_dict2["education"]):
        education = 1
        lib = ""
        if "library" in amn_dict2["education"]:
            lib = " Also there's library."
        edu_com = f"If You have or planning kids there's school and kindergarten in Your closest hood.{lib}\n"
    else:
        education = 0
        x = ["school", "kindergarten"]
        n =[]
        for a in x:
            if a not in amn_dict2['education']:
                n.append(a)

        edu_com = f"There's no {p.join(n)} for Your kids (if You have or planning ofc) near by. You will need to pick them by a car.\n"

    # Leisure
    if len(amn_dict2['leisure']) > 0:
        leisure = 1
        lei_com = f"You can spend your free time in {p.join(amn_dict2['leisure']).replace('_',' ')} not so far from Your home.\n"
    else:
        leisure = 0
        lei_com = "Even to take a breath You need to go somewhere else.\n"

    # Shop
    if len(amn_dict2['shop']) > 0:
        shop = 1
        shop_com = f"Basic grocery can by done in {p.join(amn_dict2['shop']).replace('_',' ')} quite close.\n"
    else:
        shop = 0
        shop_com = "Forget pancakes if milk just end in Your fridge. Or get a car.\n"

    # Health
    health = 0
    docoho = ["doctors", "clinic", "hospital"]
    for hel in docoho:
        if set ([hel, "dentist", "pharmacy"]) <= set(amn_dict2["health"]):
            health = 1
            hel_com = f"If you get sick or need medical treatment, buy a medicines there's close {p.join(amn_dict2['health']).replace('_',' ')}.\n"

    if health == 0:
        hel_com = []
        if len(amn_dict2["health"]) == 0:
            hel_com = ("If you get sick, need medicine or Your teeth hurt prepare for journey.\n")
        else:
            l_is = amn_dict2["health"]
            hel_com1 = f"There is {p.join(l_is)} near by"

            l_should = ["doctors", "clinic", "hospital", "dentist", "pharmacy"]
            l_no = []
            for l in l_should:
                if l not in amn_dict2["health"]:
                    l_no.append(l)

            for do in docoho:
                if do in l_is:
                    for x in docoho:
                        if x in l_no:
                            l_no.remove(x)

            hel_com2 = f" but there's no {p.join(l_no)} any close."

            hel_com = hel_com1 + hel_com2


    sum_am = food + education + leisure + shop + health + wok

    # Basic statement
    if sum_am == 6:
        comment1 = "Great! look's like You're living in 15'mins city already. Urbanist's dream come true!\n"
    elif 2 < sum_am <= 5:
        comment1 = "Almost! Sometimes you need get a car, bus or bicycle to get fast to some services.\n"
    elif 0 <= sum_am <=2:
        comment1 = "Unfortunately You need use bus, car or bicycle daily.\n"


    com = comment1 + work_com + food_com + edu_com + lei_com + shop_com + hel_com

    return com

# Color markers for map
def get_kolor(x, amn_dict):
    dict_change = {"food and drinks" : "orange", "education" : "cadetblue", "leisure" : "green", "shop" : "pink", "health" : "blue", "work" : "red"}

    kolor_dict = {}
    for key in amn_dict:
        kolor_dict[dict_change[key]] = amn_dict[key]

    for key in kolor_dict:
        if x.amenity in kolor_dict[key]:
            return key

# Plot map
def plot(loc, df_amn):

    df_amn = df_amn.fillna('-')

    lat = loc[0]
    lon = loc[1]

    # Plot maps
    map = folium.Map(location = [lat, lon], tiles = "Stamen Toner", zoom_start=14)

    # Mark user location
    folium.Circle(
        radius=50,
        location=[lat, lon],
        popup="Your location",
        color="crimson",
        fill=True,
    ).add_to(map)

    # Create a amenity list
    amenity_list = [[point.xy[1][0], point.xy[0][0]] for point in df_amn.amn_centr ]
    i = 0
    for coordinates in amenity_list:
        # Place the markers with the popup labels and data
        map.add_child(folium.Marker(location = coordinates, popup =
            str(df_amn.amenity[i]).capitalize() + ' ' + str(df_amn.name[i]) + '<br>' +
            "Adress: " + str(df_amn.street[i]) + ' ' + str(df_amn.housenumber[i]) + '<br>' +
            "Distance:  " + str(int(df_amn.shortest[i])) + ' m',
            icon = folium.Icon(color = str(df_amn.kolor[i]))))
        i = i + 1

    #Print polygons
    amn_poly = df_amn.loc[lambda x: x['geometry'].geometry.type == "Polygon", :]
    amn_poly = amn_poly[['kolor', 'geometry']]
    amn_poly.to_json()

    folium.GeoJson(
        data=amn_poly,
        style_function = lambda feature: {'fillColor': feature['properties']['kolor'], 'color': feature['properties']['kolor']}
        ).add_to(map)

    filepath = "map.html"
    map.save(filepath)
    IFrame(filepath, width = 600, height = 500)

if __name__ == "__main__":
    main()
