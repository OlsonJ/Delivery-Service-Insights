import json
import csv
import pandas as pd
import numpy as np

file_path = r"G:\...\activities.csv"

df = pd.read_csv(file_path)
df.head()
df.columns

'''
Index(['resource_state', 'athlete_id', 'athlete_resource_state', 'name',
       'distance', 'moving_time', 'elapsed_time', 'total_elevation_gain',
       'type', 'sport_type', 'workout_type', 'device_name', 'id', 'start_date',
       'start_date_local', 'timezone', 'utc_offset', 'location_city',
       'location_state', 'location_country', 'achievement_count',
       'kudos_count', 'comment_count', 'athlete_count', 'photo_count',
       'map_id', 'map_summary_polyline', 'map_resource_state', 'trainer',
       'commute', 'manual', 'private', 'visibility', 'flagged', 'gear_id',
       'start_latlng', 'end_latlng', 'average_speed', 'max_speed',
       'average_watts', 'device_watts', 'kilojoules', 'has_heartrate',
       'heartrate_opt_out', 'display_hide_heartrate_option', 'elev_high',
       'elev_low', 'upload_id', 'upload_id_str', 'external_id',
       'from_accepted_tag', 'pr_count', 'total_photo_count', 'has_kudoed'],
      dtype='object')
'''

dfc = df[['name', 'distance', 'moving_time', 'elapsed_time', 'start_latlng', 'end_latlng', 'max_speed', 'average_speed']]
dfc.head()
