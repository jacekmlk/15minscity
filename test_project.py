from project import get_location, get_amenities, order, comment
import pytest
from shapely.geometry import MultiPoint
import geopandas as gpd

def test_get_location():
    with pytest.raises(ValueError):
        get_location("")

    with pytest.raises(ValueError):
        get_location("Partyzantów")

    with pytest.raises(ValueError):
        get_location("Partyzantów, Wrocław")

    with pytest.raises(Exception):
        get_location("^[[A")

    assert get_location("Mikołaja Kopernika, 11, Wrocław") == (51.10953225, 17.085648899472343)
    assert get_location("Partyzantów, 25, Wrocław") == (51.109263, 17.097559)

def test_get_amenities():
    with pytest.raises(SystemExit):
        tag = {"amenity":"restaurant"}
        loc = (24.4146, 20.3275)
        get_amenities(loc, tag)

def test_order():
    df = gpd.GeoDataFrame(
        {
        'geometry' : [
        MultiPoint([(1, 2), (3, 4)]),
        MultiPoint([(2, 1), (0, 0)]),
        MultiPoint([(3, 1), (1, 0)])
        ],
        'name' : ['a','b','c'],
        'addr:street' : ['s1','s2','s3'],
        'addr:housenumber' : ['h1','h2','h3'],
        'amenity' : ['amn', None, None],
        'leisure' : [None, 'lei', None],
        'shop' : [None, None, 'sho'],
        'random' : ['ab', None, 'cd']
    }, crs=4326)

    df1 = gpd.GeoDataFrame(
        {
        'geometry' : [
        MultiPoint([(1, 2), (3, 4)]),
        MultiPoint([(2, 1), (0, 0)]),
        MultiPoint([(3, 1), (1, 0)])
        ],
        'name' : ['a','b','c'],
        'street' : ['s1','s2','s3'],
        'housenumber' : ['h1','h2','h3'],
        'amenity' : ['amn', 'lei', 'sho']
    }, crs=4326)

    assert order(df).equals(df1)

    df2 = gpd.GeoDataFrame(
        {
        'geometry' : [
        MultiPoint([(1, 2), (3, 4)]),
        MultiPoint([(2, 1), (0, 0)]),
        MultiPoint([(3, 1), (1, 0)])
        ],
        'name' : ['a','b','c'],
        'addr:street' : ['s1','s2','s3'],
        'addr:housenumber' : ['h1','h2','h3'],
        'shop' : [None, None, 'sho'],
        'random' : ['ab', None, 'cd']
    }, crs=4326)

    df3 = gpd.GeoDataFrame(
        {
        'geometry' : [
        MultiPoint([(1, 2), (3, 4)]),
        MultiPoint([(2, 1), (0, 0)]),
        MultiPoint([(3, 1), (1, 0)])
        ],
        'name' : ['a','b','c'],
        'street' : ['s1','s2','s3'],
        'housenumber' : ['h1','h2','h3'],
        'amenity' : [None, None, 'sho']
    }, crs=4326)

    assert order(df2).equals(df3)

def test_comment():
    amn_dict = {
        'food and drinks' : ["restaurant", "fast_food", "cafe", "bar", "pub", "ice_cream"], # At least one
        'education' : ["school", "kindergarten", "library"], # At least school and kindergarten
        'leisure' : ["theatre", "cinema", "social_centre", "park"], # At least one
        'shop' : ["marketplace", "convenience", "supermarket"], #At least one
        'health' : ["hospital", "doctors", "clinic", "pharmacy", "dentist"],
        'work' : ["workplace"]
        }

    df_amn = gpd.GeoDataFrame(
        {
            "geometry" : MultiPoint([(1, 2), (3, 4)]),
            "amenity" : "zero"
        }
    )

    assert comment(df_amn, amn_dict) =="Unfortunately You need use bus, car or bicycle daily.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "Unfortunately there's no close place to eat or drink. Forget to drink with friends and gently late walks to home.\n" \
    + "There's no school and kindergarten for Your kids (if You have or planning ofc) near by. You will need to pick them by a car.\n" \
    + "Even to take a breath You need to go somewhere else.\n" \
    + "Forget pancakes if milk just end in Your fridge. Or get a car.\n" \
    + "If you get sick, need medicine or Your teeth hurt prepare for journey.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "geometry" : MultiPoint([(1, 2), (3, 4)]),
            "amenity" : "restaurant"
        }
    )

    assert comment(df_amn, amn_dict) =="Unfortunately You need use bus, car or bicycle daily.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "There's no school and kindergarten for Your kids (if You have or planning ofc) near by. You will need to pick them by a car.\n" \
    + "Even to take a breath You need to go somewhere else.\n" \
    + "Forget pancakes if milk just end in Your fridge. Or get a car.\n" \
    + "If you get sick, need medicine or Your teeth hurt prepare for journey.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "geometry" : [ MultiPoint([(1, 2), (3, 4)]), MultiPoint([(1, 2), (3, 4)])],
            "amenity" : ["restaurant", "kindergarten"]
        }
    )

    assert comment(df_amn, amn_dict) =="Unfortunately You need use bus, car or bicycle daily.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "There's no school for Your kids (if You have or planning ofc) near by. You will need to pick them by a car.\n" \
    + "Even to take a breath You need to go somewhere else.\n" \
    + "Forget pancakes if milk just end in Your fridge. Or get a car.\n" \
    + "If you get sick, need medicine or Your teeth hurt prepare for journey.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library"]
        }
    )

    assert comment(df_amn, amn_dict) =="Unfortunately You need use bus, car or bicycle daily.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "Even to take a breath You need to go somewhere else.\n" \
    + "Forget pancakes if milk just end in Your fridge. Or get a car.\n" \
    + "If you get sick, need medicine or Your teeth hurt prepare for journey.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library", "park"]
        }
    )

    assert comment(df_amn, amn_dict) =="Almost! Somtimes you need get a car, bus or bicycle to get fast to some services.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "You can spend your free time in park not so far from Your home.\n" \
    + "Forget pancakes if milk just end in Your fridge. Or get a car.\n" \
    + "If you get sick, need medicine or Your teeth hurt prepare for journey.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library", "park", "convenience"]
        }
    )

    assert comment(df_amn, amn_dict) =="Almost! Somtimes you need get a car, bus or bicycle to get fast to some services.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "You can spend your free time in park not so far from Your home.\n" \
    + "Basic grocery can by done in convenience quite close.\n" \
    + "If you get sick, need medicine or Your teeth hurt prepare for journey.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library", "park", "convenience", "doctors", "dentist", "pharmacy"]
        }
    )

    assert comment(df_amn, amn_dict) =="Almost! Somtimes you need get a car, bus or bicycle to get fast to some services.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "You can spend your free time in park not so far from Your home.\n" \
    + "Basic grocery can by done in convenience quite close.\n" \
    + "If you get sick or need medical treatment, buy a medicines there's close doctors, pharmacy, and dentist.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library", "park", "convenience", "doctors", "dentist", "pharmacy", "workplace"]
        }
    )

    assert comment(df_amn, amn_dict) =="Great! look's like You're living in 15'mins city already. Urbanist's dream come true!\n" \
    + "You work nearly where You live. Enjoy daily walks!\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "You can spend your free time in park not so far from Your home.\n" \
    + "Basic grocery can by done in convenience quite close.\n" \
    + "If you get sick or need medical treatment, buy a medicines there's close doctors, pharmacy, and dentist.\n"

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library", "park", "convenience", "doctors"]
        }
    )

    assert comment(df_amn, amn_dict) =="Almost! Somtimes you need get a car, bus or bicycle to get fast to some services.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "You can spend your free time in park not so far from Your home.\n" \
    + "Basic grocery can by done in convenience quite close.\n" \
    + "There is doctors near by but there's no dentist and pharmacy any close."

    df_amn = gpd.GeoDataFrame(
        {
            "amenity" : ["restaurant", "kindergarten", "school", "library", "park", "convenience", "pharmacy"]
        }
    )

    assert comment(df_amn, amn_dict) =="Almost! Somtimes you need get a car, bus or bicycle to get fast to some services.\n" \
    + "Every day You lost Your precious time in daily commute\n" \
    + "If You wanna go outside to eat something, or meet with friends there is restaurant near by.\n" \
    + "If You have or planning kids there's school and kindergarten in Your closest hood. Also there's library.\n" \
    + "You can spend your free time in park not so far from Your home.\n" \
    + "Basic grocery can by done in convenience quite close.\n" \
    + "There is pharmacy near by but there's no doctors, clinic, hospital, and dentist any close."
