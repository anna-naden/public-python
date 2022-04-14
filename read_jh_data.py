""" read JH data """
import csv
import sys
from get_config import get_config
def read_jh_data():
    """ read JH data """
    config = get_config()
    try:
        with open(config['FILES']['world_covid_deaths'], 'rt', \
            newline='', encoding='utf-8') as fread:
            reader = csv.reader(fread)
            death_lines = list(reader)
        with open(config['FILES']['world_covid_cases'], 'rt', \
            newline='', encoding='utf-8') as fread:
            reader = csv.reader(fread)
            cases_lines = list(reader)
        with open(config['FILES']['us_covid_deaths'], 'rt', \
            newline='', encoding='utf-8') as fread:
            reader = csv.reader(fread)
            us_death_lines = list(reader)
        with open(config['FILES']['us_covid_cases'], 'rt', \
            newline='', encoding='utf-8') as fread:
            reader = csv.reader(fread)
            us_cases_lines = list(reader)
    except FileNotFoundError as inst:
        print(inst)
        sys.exit(1)
    assert (len(us_death_lines)==len(us_cases_lines))
    assert (len(cases_lines) == len(death_lines))
    return death_lines, cases_lines, us_death_lines, us_cases_lines
