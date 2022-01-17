# HDB_Resale_Visuals
Data Visualization for 4-Room Resale Flats in Singapore  

# Description 
The hdb_visual.py script collects resale data from https://data.gov.sg/dataset/resale-flat-prices, and generate a map with the help of folium.  
1. Data of all 4-Room Resale Flat from 2017 is collected from the data.gov database.  
2. Coordinates of these flats are gotten with the help of one-map api.  
3. These flats are placed into 'boxes' based on their coordinates, by rounding down to a specific size.  
4. Within each 'box' the data is aggregated 
5. These boxes are then plotted as a feature collection in folium.
6. Colormap is added from Branca for data visualization

# Result
![image](https://user-images.githubusercontent.com/80518234/149754423-4d79ba7a-9a09-4257-b685-777350ee922a.png)
![image](https://user-images.githubusercontent.com/80518234/149754461-ac8b5104-270d-4756-b8b0-ed98f35b9a0f.png)
