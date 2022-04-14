import numpy as np
import json
import pandas as pd
import time
from get_config import get_config
from sample import sample_us_df

cases_or_deaths='c'
start = time.time()
config = get_config()
df_us = pd.read_pickle('us_state_county_date.pickle')
end_date = df_us.index.get_level_values('date').max()

n_days_map = int(config['MAPS']['n_days_cases'])
start_date = end_date-np.timedelta64(n_days_map,'D')
print(f'states features date range {str(start_date)[:10]} {str(end_date)[:10]}')
state_cases = {}
    
#USA
states = df_us.index.get_level_values('state').unique()
for state in states:
    dates, counts, population, UIDs = sample_us_df(df_us, state=state, delta=True)

    # The Johns Hopkins data has incorrect FIPS code for unassigned county in Illinois, so instead of keying on FIPS I must key on state name, e.g. Illinois
    state_name = state
    print(state_name)
    date_index1 = np.where(dates==start_date)[0]
    date_index2 = np.where(dates==end_date)[0]
    counts1 = counts[date_index1]
    counts2 = counts[date_index2]
    fips = UIDs[0][3:5]
    state_cases['USA' + fips]=1e5*(counts2-counts1)/(population*n_days_map)

with open(config['FILES']['states_geometry'], 'r') as f_usa:
    us_feature_dict = json.load(f_usa)

for feature in us_feature_dict['features']:
    fid = 'USA' + feature['properties']['STATE']
    if fid in state_cases.keys():
        feature['id'] = fid
        cases = state_cases[feature['id']]
        feature['properties']['density'] = f'{cases}'
        feature['properties']['fips'] = fid
feature_dict = us_feature_dict

with open('/var/www/html/all-states.json', 'wt') as f:
    json.dump(feature_dict, f)
f.close()
end = time.time()
seconds = round(end-start,1)
print(f'\nStates features made. Elapsed time {seconds:0.1f} secs')