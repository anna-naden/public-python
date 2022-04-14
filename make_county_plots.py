""" Make state plot images """
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from sample import sample_us_df
from get_config import get_config
import time

start = time.time()
cases_or_deaths = 'c'
matplotlib.use('Agg')
config = get_config()
data_frame = pd.read_pickle('us_state_county_date.pickle')
states = data_frame.index.get_level_values('state').unique()
MAX_Y = float(config['PLOT CONFIGURATION']['max_y'])
dates_us, counts_us, population_us, UIDs = sample_us_df(data_frame, delta=True, cases_or_deaths=cases_or_deaths)
for state in states:
    print(state)
    df_state = data_frame[data_frame.index.get_level_values(0)==state]
    counties = df_state.index.get_level_values(1).unique()
    dates_state, counts_state, populations_state, UIDs_state = sample_us_df(df_state, delta=True, cases_or_deaths=cases_or_deaths)
    for county in counties:
        dates_county, counts_county, populations_county, UIDs_county = sample_us_df(data_frame, state=state, county=county, delta=True, cases_or_deaths=cases_or_deaths)
        if populations_county[0] != 0 and np.max(counts_county) != 0:
            #print(f'\t{county}')
            assert dates_county == dates_us
            #make plot
            fig, ax=plt.subplots(figsize=(4.5,2.4), constrained_layout=True)
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)
            ax.plot(dates_county, 1e5*(counts_county/populations_county[0]))
            ax.plot(dates_us, 1e5*(counts_us/population_us[0]))
            ax.set_ylim(0, MAX_Y)
            ax.legend([county, 'USA'])
            entity = 'Fatalities'
            if cases_or_deaths == 'c':
                entity = 'Cases'
            ax.set_title(f'{entity} per 100,000 Population', fontsize=9)

            #Put text showing last date and last value
            last = len(counts_county)-1
            last_date=f'{dates_county[last]}'[:10]
            xc = dates_county[last]
            yc = 1e5*(counts_county[last]/populations_county[0])
            Y_TEXT = -36
            if yc< float(config['PLOT CONFIGURATION']['max_y'])/2:
                Y_TEXT = 0
            ax.annotate(f'{last_date}, {round(counts_county[last],4)}', [xc,yc],
                xytext=(-72, Y_TEXT), textcoords='offset points',
                arrowprops=dict(arrowstyle="->"))

            #save and upload
            fig.savefig('/var/www/html/' +  UIDs_county[0][3:] + '.jpg')
            #plt.show()
            plt.close()
print(time.time()-start)