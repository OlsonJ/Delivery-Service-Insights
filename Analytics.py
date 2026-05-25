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

'''
name	distance	moving_time	elapsed_time	start_latlng	end_latlng	max_speed	average_speed
0	Food delivery ride	22767.3	6907	13600	[25.802302, -80.198495]	[25.801242, -80.190936]	12.42	3.296
1	Tdap shot food delivery	11498.1	2751	4543	[25.795003, -80.218614]	[25.801973, -80.198074]	12.24	4.180
2	Warmup service - phone overheated	1793.6	456	885	[25.805983, -80.188097]	[25.801934, -80.198103]	9.58	3.933
3	Service 516	15196.9	4278	10807	[25.802605, -80.1936]	[25.824401, -80.214399]	13.40	3.552
4	Water bottle dropped:(	13429.1	3777	5909	[25.799927, -80.196323]	[25.801853, -80.198158]	11.48	3.555
'''
