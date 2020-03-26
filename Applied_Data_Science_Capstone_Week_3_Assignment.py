#!/usr/bin/env python
# coding: utf-8

# In[443]:


from bs4 import BeautifulSoup
import requests
import numpy as np
import pandas as pd
from geopy.geocoders import Nominatim
import folium
import json
from pandas.io.json import json_normalize
from sklearn.cluster import KMeans
import matplotlib.cm as cm
import matplotlib.colors as colors

url = 'https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M'
result = requests.get(url)


# #### Loading Wikipedia table

# In[429]:


soup = BeautifulSoup(result.content, 'html.parser')
table = soup.find('table')


# #### Extracting the data from Wikipedia

# In[430]:


data = []

for tr in table.find_all('tr'):
    for td in tr.find_all('td'):
        td_text = td.get_text().strip()
        n = 0
        postalcode = td_text[n:3]
        borough = td_text[3::].split("(")[0]
        try:
            neighborhood = td_text[3:-1].split("(")[1]
        except IndexError:
            neighborhood = ""
        data.append([postalcode, borough, neighborhood])
        n += 1


# #### Replacing the column names

# In[432]:


cols = ['PostalCode', 'Borough', 'Neighborhood']
df = pd.DataFrame(data, columns=cols)

df.head()


# #### Replacing '/' values with ','

# In[322]:


df["Neighborhood"] = df["Neighborhood"].str.replace(' /', ', ')

df.head()


# #### Removing 'Not assigned' values from the Borough column

# In[420]:


df_drop = df[df.Borough != 'Not assigned']


# #### Checking for empty cells in the 'Neighborhood' column

# In[421]:


df_drop.loc[df_drop['Neighborhood'] == '']


# #### Resetting the index

# In[422]:


df_drop = df_drop.reset_index(drop=True)


# In[ ]:





# In[398]:


for x in df_drop['Borough']:
    new_value = x.split("/")
    if df_drop['Neighborhood'].empty:
        df_drop['Borough'] = new_value[0]
        try:
            df_drop['Neighborhood'] = new_value[1]
        except IndexError:
            df_drop['Neighborhood'] = df_drop['Neighborhood']


# #### Replacing empty values in 'Borough' column

# In[424]:


df_drop['Neighborhood'] = df_drop['Neighborhood'].replace('', df_drop['Borough'])


# #### Checking the dataframe shape

# In[427]:


df_drop.shape


# #### Loading the CSV and renaming the columns

# In[433]:


dfgeo = pd.read_csv("Geospatial_Coordinates.csv")
dfgeo.rename(columns={'Postal Code': 'PostalCode'}, inplace=True)


# #### Merging the dataframes

# In[437]:


df2 = pd.merge(df_drop, dfgeo, on="PostalCode", how='left')


# In[438]:


df2.head()


# #### Checking the geographical coordinate of the City of Torronto.

# In[439]:


address = 'Toronto, Canada'

geolocator = Nominatim()
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of the City of Toronto are {}, {}.'.format(latitude, longitude))


# #### Create map of Torronto using latitude and longitude values

# In[442]:


map_toronto = folium.Map(location=[latitude, longitude], zoom_start=10)

# add markers to map
for lat, lng, borough, neighborhood in zip(df2['Latitude'], df2['Longitude'], df2['Borough'], df2['Neighborhood']):
    label = '{}, {}'.format(neighborhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=3,
        popup=label,
        color='green',
        fill=True,
        fill_color='#3199cc',
        fill_opacity=0.3,
        parse_html=False).add_to(map_toronto)  
    
map_toronto


# In[ ]:




