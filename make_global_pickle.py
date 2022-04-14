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
import sys
from datetime import datetime
import time
import numpy as np
import pandas as pd
from read_jh_data import read_jh_data
from get_config import get_config

def convert_date(date_str):
    """ convert dates from string"""
    str1 = date_str.split('/')
    if len(str1[0])==1:
        str1[0] = '0'+str1[0]
    if len(str1[2])==2:
        str1[2] = '20'+str1[2]
    date_str = '/'.join(str1)
    return datetime.strptime(date_str, "%m/%d/%Y")
def parse_jh_cases(lines):
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
    data, index_state, index_country = \
        make_data_cases(tags, counts, header_indices)
    data_frame = pd.DataFrame(data, index=[index_country, index_state, dates_list],\
       columns=['counts'])
    data_frame.index.names=['country','state', 'date']
    return data_frame
def make_data(tags, counts, header_indices):
    """ For deaths, construct data and indices for Pandas data frame """
    index_state = []
    index_country=[]
    lats = []
    lons = []
    for tag in tags:
        lat = tag[header_indices['Lat']]
        lon = tag[header_indices['Long']]
        for _ in range(counts.shape[1]):
            index_state.append(tag[header_indices['Province/State']])
            index_country.append(tag[header_indices['Country/Region']])
            lats.append(lat if lat != "" else 0)
            lons.append(lon if lon != "" else 0)
    data = np.transpose(\
        np.vstack([\
        lats,\
        lons,\
        counts.flatten()])\
        )
    return data, index_state, index_country
def make_data_cases(tags, counts, header_indices):
    """ For cases, construct data and indices for Pandas data frame """
    index_state = []
    index_country=[]
    for tag in tags:
        for _ in range(counts.shape[1]):
            index_state.append(tag[header_indices['Province/State']])
            index_country.append(tag[header_indices['Country/Region']])
    data = np.transpose(\
        np.vstack([\
        counts.flatten()])\
        )
    return data, index_state, index_country
def get_pops():
    """ Get data frame with populations of countries worldwide """
    config = get_config()
    try:
        data_frame=pd.read_csv(config['FILES']['world_census'], sep=',')
    except FileNotFoundError:
        return None
    data_frame.columns=['country', 'country_code','population', 'region']
    data_frame.drop('country_code', axis='columns')
    data_frame.drop('region', axis='columns')
    data_frame.set_index(['country','country_code'], inplace=True)
    return data_frame
def parse_jh_deaths(counts):
    """ Parse jh data
    Args: raw lines from csv file
    Returns:
        deaths: numpy array (counties x dates)
        dates: 1d array of dates; type is datetime.datestime
        tag_list: list of tag dictionaries, one for each county
        states_counties: 2d array (the i-th row contains
        two elements: the i-th state and the i-th county)
    """
    header = counts[0,:4]
    dates = counts[0,4:]
    dates = np.array(list(map(convert_date,dates)))

    header_indices = {}
    for i, header1 in enumerate(header):
        header_indices[header1] = i

    #The part of the spreasheet after the first row, with all
    #the columns up to but not including dates
    tags=list(counts[1:,:4])
    counts = counts[1:,4:]
    assert counts.shape[1] == dates.shape[0]
    dates_list = list(dates)*counts.shape[0]
    data, index_state, index_country = \
        make_data(tags, counts, header_indices)
    data_frame = pd.DataFrame(data, index=[index_country, index_state, dates_list],\
       columns=['lat','lon','counts'])
    data_frame.index.names=['country','state','date']
    return data_frame
start = time.time()
death_lines1, cases_lines1, _, _ = read_jh_data()

data_frame1 = parse_jh_deaths(np.array(death_lines1))
data_frame1.lat = data_frame1.lat.astype(float)
data_frame1.lon = data_frame1.lon.astype(float)
data_frame1.counts = data_frame1.counts.astype(float)
data_frame_pops = get_pops()
if data_frame_pops is None:
    print('error reading pops')
    sys.exit(1)
data_frame1 = data_frame1.join(data_frame_pops, how='left')

data_frame2 = parse_jh_cases(cases_lines1)
data_frame2.counts = data_frame2.counts.astype(float)
data_frame2 = data_frame2.assign(lat=0)
data_frame2 = data_frame2.assign(lon=0)

data_frame3 = data_frame1.join(data_frame2, how='outer', lsuffix='_d', rsuffix='_c')
data_frame3.rename(columns={'population_d':'population', 'country_l':'country'}, inplace=True)
data_frame3.population.replace(np.nan, 1, inplace=True)
data_frame3.population = data_frame3.population.astype(int)
data_frame3.population.replace(1, np.nan, inplace=True)
data_frame3.to_pickle('global_pickle.pickle')

print(time.time()-start)
