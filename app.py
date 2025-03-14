import streamlit as st
import requests
import datetime as dt
import pandas as pd
import math

st.set_page_config(
    page_title = "New-York taxi",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded",
)

'''
# New-York taxi
'''

'''
## Parameters
'''
'''
### When do you go ?
'''
pickup_date= st.date_input(
    "When are you go?",
    dt.datetime.now(dt.timezone(dt.timedelta(hours=-5)))
)
pickup_time= st.time_input(
    "At what time?",
    dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))),
    step = dt.timedelta(minutes=5)
)
pickup_datetime = dt.datetime.combine(pickup_date, pickup_time)

''' ### How many passengers ?'''
passenger_count = st.number_input('Number', min_value= 1, max_value= 8,step = 1)

'''
### Your itinerary
'''
# Get adresse:
# lon, lat baseline
min_lon, max_lon = -74.3,-73.7
avg_lon = (min_lon+max_lon)/2
min_lat, max_lat = 40.5, 40.9
avg_lat = (min_lat+max_lat)/2

@st.cache_resource
def get_coordinate_2(address):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        'q': address,
        'format' : 'json'
    }
    headers = {'User-Agent': "My demo geomap app"}
    response = requests.get(url,params = params, headers=headers).json()
    if response:
        res = pd.DataFrame(response)
        res['lat'] = res['lat'].map(float)
        res['lon'] = res['lon'].map(float)
        idx = (res['lon'] <=max_lon) & (res['lon'] >=min_lon) & (res['lat'] <=max_lat) & (res['lat'] >=min_lat)
        res = res[idx]
        if res.empty :
            st.write("❌ Sorry, your adress is out of perimeter")
            return None
        else :
            return res
    else :
        st.write("❌ Sorry, we don't find your adress")

left, right = st.columns(2)
left.write('''
#### From :
''')
pickup_adress_text = left.text_input('Where are you leaving from ?', 'Central Park')
if pickup_adress_text != None :
    pickup_adress_df = get_coordinate_2(pickup_adress_text)
    pickup_adress_dn = left.selectbox('Select the pickup address',pickup_adress_df['display_name'])
    pickup_longitude = pickup_adress_df[pickup_adress_df['display_name'] == pickup_adress_dn ]['lon'][0]
    pickup_latitude = pickup_adress_df[pickup_adress_df['display_name'] == pickup_adress_dn ]['lat'][0]

right.write('''
#### To :
''')
dropoff_adress_text = right.text_input('Where are you going ?', 'Brooklyn')
if dropoff_adress_text != None :
    dropoff_adress_df = get_coordinate_2(dropoff_adress_text)
    dropoff_adress_dn = right.selectbox('Select the dropoff address',dropoff_adress_df['display_name'])
    dropoff_longitude = dropoff_adress_df[dropoff_adress_df['display_name'] == dropoff_adress_dn ]['lon'][0]
    dropoff_latitude = dropoff_adress_df[dropoff_adress_df['display_name'] == dropoff_adress_dn ]['lat'][0]

if dropoff_adress_text != None and pickup_adress_text != None and st.button('Show on a map') :
    '''
    #### Your cab trip
    '''
    # Draw map
    coordinates = pd.concat([
        dropoff_adress_df[dropoff_adress_df['display_name'] == dropoff_adress_dn ],
        pickup_adress_df[pickup_adress_df['display_name'] == pickup_adress_dn ]
    ])[['lon','lat']]
    st.map(data=coordinates, latitude = avg_lat, longitude = avg_lon, zoom = 10, size = 500, )
##################### Prediction ######################
@st.cache_resource
def predict(params):
    url = 'https://taxifare-326525614739.europe-west1.run.app/predict'
    response = requests.get(url,params=params).json()
    return response

def manhattan_distance(start_lat: float=pickup_latitude, start_lon: float=pickup_longitude, end_lat: float=dropoff_latitude, end_lon: float=dropoff_longitude) -> float:
    """
    Calculate the Manhattan distance between in km two points on the earth (specified in decimal degrees).
    """
    earth_radius = 6371

    lat_1_rad, lon_1_rad = math.radians(start_lat), math.radians(start_lon)
    lat_2_rad, lon_2_rad = math.radians(end_lat), math.radians(end_lon)

    dlon_rad = lon_2_rad - lon_1_rad
    dlat_rad = lat_2_rad - lat_1_rad

    manhattan_rad = abs(dlon_rad) + abs(dlat_rad)
    manhattan_km = manhattan_rad * earth_radius

    return manhattan_km

params = {
        'pickup_datetime': pickup_datetime,
        'pickup_longitude': pickup_longitude,
        'pickup_latitude': pickup_latitude,
        'dropoff_longitude': dropoff_longitude,
        'dropoff_latitude': dropoff_latitude,
        'passenger_count': passenger_count
    }

if st.button('# Get price!', type='primary', use_container_width=True):
    result = predict(params)
    km = manhattan_distance(pickup_latitude,pickup_longitude,dropoff_latitude,dropoff_longitude)
    f'''
    ### The selected itinerary should cost you **{round(float(result['fare']),2)} $** for {round(km)} km as the crow flies
    '''
# '''

# 2. Let's build a dictionary containing the parameters for our API...

# 3. Let's call our API using the `requests` package...

# 4. Let's retrieve the prediction from the **JSON** returned by the API...

# ## Finally, we can display the prediction to the user
# '''
