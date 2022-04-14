""" Make state plot images """
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from sample import sample_us_df
from get_config import get_config
import time

start = time.time()
config = get_config()
matplotlib.use('Agg')
data_frame = pd.read_pickle('us_state_county_date.pickle')
states = data_frame.index.get_level_values(0).unique()
MAX_Y = float(config['PLOT CONFIGURATION']['max_y'])
cases_or_deaths='d'
dates_us, counts_us, population_us, UIDs = sample_us_df(data_frame, delta=True, cases_or_deaths=cases_or_deaths)
for state in states:
    print(state)
    dates, counts, population, UIDs = sample_us_df(data_frame, state=state, delta=True, cases_or_deaths=cases_or_deaths)
    if population[0] != 0:
        assert dates == dates_us
        #make plot
        fig, ax=plt.subplots(figsize=(3,3), constrained_layout=True)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        ax.plot(dates, 1e5*counts/population[0])
        ax.plot(dates_us, 1e5*counts_us/population_us[0])
        ax.set_ylim(0, MAX_Y)
        ax.legend([state, 'USA'])
        ax.set_title('Daily Counts per 100,000 Population', fontsize=9)

        #Put text showing last date and last value
        last = len(counts)-1
        last_date=f'{dates[last]}'[:10]
        xc = dates[last]
        yc = 1e5*counts[last]/population[0]
        Y_TEXT = -36
        if yc< float(config['PLOT CONFIGURATION']['max_y'])/2:
            Y_TEXT = 0
        ax.annotate(f'{last_date}, {round(counts[last],4)}', [xc,yc],
            xytext=(-72, Y_TEXT), textcoords='offset points',
            arrowprops=dict(arrowstyle="->"))

        #save and upload
        fips = UIDs[0][3:5]
        fig.savefig('/var/www/html/' +  fips + '.jpg')
        #plt.show()
        plt.close()
print(time.time()-start)