import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import numpy as np

class ht_card:
    # Heat treatment card magic numbers
    min_load_temp = 300 #F - minimal temperature before heat treatment should start
    cooling_end_temp = 400
    sr_nominal_temp = 1050 #F
    sr_nominal_temp_deviation = 25 #F
    sr_min_temp = sr_nominal_temp-sr_nominal_temp_deviation
    sr_max_temp = sr_nominal_temp+sr_nominal_temp_deviation
    max_heating_rate = 172 #F/hour  #!!!
    max_cooling_rate = 172 #F/hour
    sr_min_duration_rec = dt.time(hour = 3, minute = 30)
    sr_max_duration_rec = dt.time(hour = 4, minute = 30)
    sr_min_duration_acceptable = dt.time(hour = 3)
    sr_max_duration_acceptable = dt.time(hour = 4)
    index_buffer = 10 # imperical number

class ht_channel:
    sr_duration = dt.time()

class ht_chart:
    reference_point_index_dict = list()
    channel = {'top': ht_channel(), 'btn': ht_channel()}


def find_reference_points (df, column_name, ht_card):
    ch_data = np.array(df[column_name])  # channel data
    heating_start_index = np.argmax(ch_data >= ht_card.min_load_temp) - 1
    # print(ch_data[heating_start_index ], ' ', heating_start_index )

    sr_start_index = np.argmax(ch_data > ht_card.sr_min_temp)
    # print(ch_data[sr_start_index ], ' ', sr_start_index)

    sr_data = ch_data[sr_start_index:]
    sr_end_index_relative = np.argmax(sr_data <= ht_card.sr_min_temp)
    sr_end_index = sr_end_index_relative + sr_start_index
    # print(ch_data[sr_end_index],' ',sr_end_index)

    cooling_end_index_relative = np.argmax(sr_data < ht_card.cooling_end_temp)
    cooling_end_index = cooling_end_index_relative + sr_start_index
    # print(ch_data[cooling_end_index],' ',cooling_end_index)
    reference_point_index_dict = {'heating_start_index':heating_start_index, 'sr_start_index':sr_start_index, 'sr_end_index':sr_end_index, 'cooling_end_index':cooling_end_index}
    return reference_point_index_dict;





#------------------Reading raw data from file------------------
#Selection of file to read
#from tkinter import filedialog
#csv_path = filedialog.askopenfilename()
#data_table = pd.read_csv(filepath_or_buffer=csv_path)
#print(csv_path)

number_of_colums_to_read = 6
chanel_names_list = ['Program','Oven','Top','Bottom']
column_names_list = list(chanel_names_list)
column_names_list.insert(0,'Date')
redundant_program_column_name = 'Program1'
column_names_list.insert(2,redundant_program_column_name)
#['Date','Program','Program1','Oven','Top','Bottom'] #Names for data columns

file_to_read = '17H008.csv' #csv file name

data_table = pd.read_csv(file_to_read, usecols=range(number_of_colums_to_read)) #reads raw data from csv file
data_table.columns = column_names_list
#Delete second column of programm set temperature
del data_table[redundant_program_column_name]

#------------------Data preparations------------------

# Changing Excel Date/Time format to  Python datetime format
import xlrd
PyDate = pd.Series(data_table.Date)
#!!! that should be fixed -> it should be the way to treat it as a vector, not a list of individual number
for i in range(len(data_table.Date)):
    PyDate[i] = xlrd.xldate.xldate_as_datetime(data_table.Date[i], 0)  # Datemode = 0
data_table.Date = PyDate


# Finding significant points on graph
ef_sr_card = ht_card()
ef_sr = ht_chart()
point_dict_top= find_reference_points(data_table, 'Top', ef_sr_card)
point_dict_btn = find_reference_points(data_table, 'Bottom', ef_sr_card)

# Finding heat rates
date = np.array(data_table['Date'][point_dict_top['heating_start_index']: point_dict_top['sr_start_index']]) # array of dates
heating = np.array(data_table['Top'][point_dict_top['heating_start_index']: point_dict_top['sr_start_index']]) #array of temperatures
keep_going = True
prev_timepoint = date[0]
print(prev_timepoint)
heat_rate_list = ()
while keep_going:
    timepoint = prev_timepoint + dt.timedelta(hours=1)
    print(timepoint)
    if timepoint > date[-1]:
        keep_going = False
    else:
        prev_timepoint = timepoint

# Finding stress relief duration

ef_sr.channel['top'].sr_duration = data_table['Date'][point_dict_top['sr_end_index']] - data_table['Date'][point_dict_top['sr_start_index']]
ef_sr.channel['btn'].sr_duration = data_table['Date'][point_dict_btn['sr_end_index']] - data_table['Date'][point_dict_btn['sr_start_index']]

print('Stress relief duration (Top):    ', ef_sr.channel['top'].sr_duration)
print('Stress relief duration (Bottom): ', ef_sr.channel['btn'].sr_duration)

# ------------------Plotting the data------------------
#
# #Adding line on graph for each chanel
# for i in range(len(chanel_names_list)):
#     plt.plot(data_table['Date'], data_table[chanel_names_list[i]], label=chanel_names_list[i])
#
# plt.grid() #turn on grid
#
# plt.legend(chanel_names_list)
# plt.xlabel('Date/Time')
# plt.ylabel('Temperature, F')
#
#
# #plt.figure(num=None, figsize=(8, 6)) #changing plot field size
# plt.show()








