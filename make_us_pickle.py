"""Read the four spreadsheets that are downloaded nightly from the Johns Hopkind website
Create the following files:
  and the value is an array of cases
- 'us_cases_tags.pkl' - a Python pickle of a list of tag arrays, one
   array for each state/county combination
- us_deaths_tags.pkl - Like us_cases_tags but for deaths instead of cases
- states_counties_cases.npy - A Numpy pickle of
- states_counties_deaths.npy - Like states_counties_cases.npy but for deaths instead of cases
- us_state_county_date_cases.pickle - A Pandas pickle with four columns: State, county, date, #cases
- us_state_county_date_deaths.pickle - Like us_state_county_date_cases.pickle,
  but for deaths instead of cases
"""
from datetime import datetime
import time
import numpy as np
import pandas as pd
from read_jh_data import read_jh_data

def convert_date(date_str):
    """ convert dates from string"""
    str1 = date_str.split('/')
    if len(str1[0])==1:
        str1[0] = '0'+str1[0]
    if len(str1[2])==2:
        str1[2] = '20'+str1[2]
    date_str = '/'.join(str1)
    return datetime.strptime(date_str, "%m/%d/%Y")
def parse_jh_us_cases(lines):
    """ Parse jh data
    Args: raw lines from csv file
    Returns:
        cases: numpy array (counties x dates). type is int64
        dates: 1d array of dates; type is datetime.datestime
        tag_list: list of tag dictionaries, one for each county
        states_counties: 2d array (the i-th row contains two elements:
        the i-th state and the i-th county)
    """
    counts = np.array(lines)
    header = counts[0,:11]
    dates = counts[0,11:]
    dates = np.array(list(map(convert_date,dates)))

    header_indices = {}
    for i, header1 in enumerate(header):
        header_indices[header1] = i

    #The part of the spreasheet after the first row, with all
    #the columns up to but not including dates
    tags=list(counts[1:,:11])
    counts = counts[1:,11:]
    assert counts.shape[1] == dates.shape[0]
    dates_list = list(dates)*counts.shape[0]
    assert counts.shape[1] == dates.shape[0]
    dates_list = list(dates)*counts.shape[0]
    data, index_state, index_county = \
        make_data_cases(tags, counts, header_indices)
    data_frame = pd.DataFrame(data, index=[index_state,index_county, dates_list],\
       columns=['UID','counts'])
    data_frame.index.names=['state','county','date']
    return data_frame
def make_data(tags, counts, header_indices):
    """ For deaths, construct data and indices for Pandas data frame """
    index_state = []
    index_county = []
    populations = []
    lats = []
    lons = []
    uid_s = []
    for tag in tags:
        for _ in range(counts.shape[1]):
            index_state.append(tag[header_indices['Province_State']])
            index_county.append(tag[header_indices['Combined_Key']])
            populations.append(tag[header_indices['Population']])
            uid_s.append(tag[header_indices['UID']])
            lats.append(tag[header_indices['Lat']])
            lons.append(tag[header_indices['Long_']])
    data = np.transpose(\
        np.vstack([\
        lats,\
        lons,\
        populations,\
        uid_s,
        counts.flatten()])\
        )
    return data, index_state, index_county
def make_data_cases(tags, counts, header_indices):
    """ For cases, construct data and indices for Pandas data frame """
    index_state = []
    index_county = []
    uid_s = []
    #fips_s = []
    for tag in tags:
        for _ in range(counts.shape[1]):
            index_state.append(tag[header_indices['Province_State']])
            index_county.append(tag[header_indices['Combined_Key']])
            uid_s.append(tag[header_indices['UID']])
            #fips_s.append(tag[header_indices['FIPS']])
    data = np.transpose(\
        np.vstack([\
        uid_s,\
        #fips_s,\
        counts.flatten()])\
        )
    return data, index_state, index_county
def parse_jh_us_deaths(counts):
    """ Parse jh data
    Args: raw lines from csv file
    Returns:
        deaths: numpy array (counties x dates)
        dates: 1d array of dates; type is datetime.datestime
        tag_list: list of tag dictionaries, one for each county
        states_counties: 2d array (the i-th row contains
        two elements: the i-th state and the i-th county)
    """
    header = counts[0,:12]
    dates = counts[0,12:]
    dates = np.array(list(map(convert_date,dates)))

    header_indices = {}
    for i, header1 in enumerate(header):
        header_indices[header1] = i

    #The part of the spreasheet after the first row, with all
    #the columns up to but not including dates
    tags=list(counts[1:,:12])
    counts = counts[1:,12:]
    assert counts.shape[1] == dates.shape[0]
    dates_list = list(dates)*counts.shape[0]
    data, index_state, index_county = \
        make_data(tags, counts, header_indices)
    data_frame = pd.DataFrame(data, index=[index_state,index_county, dates_list],\
       columns=['lat','lon','population','UID','counts'])
    data_frame.index.names=['state','county','date']
    return data_frame
start = time.time()
_, _, us_death_lines1, us_cases_lines1 = read_jh_data()
data_frame1 = parse_jh_us_deaths(np.array(us_death_lines1))
data_frame1.lat = data_frame1.lat.astype(float)
data_frame1.lon = data_frame1.lon.astype(float)
data_frame1.counts = data_frame1.counts.astype(float)
data_frame1.population = data_frame1.population.astype(int)

data_frame2 = parse_jh_us_cases(us_cases_lines1)
assert data_frame2.shape[0]==data_frame1.shape[0]
data_frame2.counts = data_frame2.counts.astype(float)
data_frame2 = data_frame2.assign(population=data_frame1.population.values)
data_frame2 = data_frame2.assign(lat=data_frame1.lat.values)
data_frame2 = data_frame2.assign(lon=data_frame1.lon.values)

data_frame3 = data_frame1.join(data_frame2, how='outer', lsuffix='_d', rsuffix='_c')
data_frame3.rename(columns={'population_d':'population', \
    'UID_d': 'UID', 'state_d':'state', 'county_d': 'county', 'lat_d':'lat', 'lon_d': 'lon'}, inplace=True)
data_frame3.drop(['population_c','lon_c', 'lat_c', 'UID_c'], axis='columns', inplace=True)
data_frame3.to_pickle('us_state_county_date.pickle')

print(time.time()-start)
