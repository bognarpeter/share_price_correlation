#!/usr/bin/env python3

import datetime
from datetime import datetime as dt
import pandas as pd
import numpy as np
import argparse
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def interpolate(series):
    df = pd.DataFrame(series)
    complete = df.interpolate(limit_direction='both').values.tolist()
    return [i for sublist in complete for i in sublist]

def process_file(fname):
    data = {}
    with open(fname) as f:
        for line in f:
            if line:
                stripped_line = line.strip()
                splitted_line = stripped_line.split('\t')
                date = dt.strptime(splitted_line[0], '%Y-%m-%d')
                date_formatted = date.strftime('%Y-%m-%d')
                value = float(splitted_line[1].replace(',','.'))
                data[date_formatted] = value

    return data

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--type', choices = ['isp', 'mps', 'uni'], default='ips', help='Type of the data to compare with ita_gov [isp/mps/uni]')
parser.add_argument('-s', '--start', default='2000-01-01', help='From date, form ex.: 2000-01-01')
parser.add_argument('-e', '--end', default='2000-01-01', help='To date, form ex.: 2000-01-01')
options = parser.parse_args()

type = options.type
start = options.start
end = options.end

ita_gov_data = process_file('./data/ita_gov.tsv')
compare_data = process_file('./data/' + type + '.tsv')

start_date = dt.strptime(start , '%Y-%m-%d')
end_date = dt.strptime(end , '%Y-%m-%d')
delta = datetime.timedelta(days=1)


ita_gov_series = []
compare_series = []
dates = []
d = start_date
while d <= end_date:
    date_i = d.strftime('%Y-%m-%d')
    dates.append(d)
    ita_gov_series.append(ita_gov_data.get(date_i, np.nan))
    compare_series.append(compare_data.get(date_i, np.nan))
    d += delta

# linear interpolation for missing values
ita_gov_complete = interpolate(ita_gov_series)
compare_complete = interpolate(compare_series)
# calculate coef. matrix
coef_matrix = np.corrcoef(ita_gov_complete, compare_complete)

# printing results
print('================')
print('From: ' + str(start_date.strftime('%Y-%m-%d')) + ' to: ' + str(end_date.strftime('%Y-%m-%d')))
print('ita gov VS. ' + type)
print('Pearson correlation: ' + str(coef_matrix[0, 1]))
print('================')

# plotting the data
date_as_num = matplotlib.dates.date2num(dates)

plt.subplot(2, 1, 1)
plt.plot(date_as_num, ita_gov_complete, 'r')
plt.title('date')
plt.ylabel('%')
plt.title('ITA GOV vs. ' + type.upper())

plt.subplot(2, 1, 2)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.plot(date_as_num, compare_complete, 'b')
plt.gcf().autofmt_xdate()
plt.xlabel('date')
plt.ylabel('share_pirces')

plt.show()
