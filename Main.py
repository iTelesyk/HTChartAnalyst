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

class ht_cl_curve: #heating cooling data
    def __init__(self):
        self.timepoints =  np.array([])
        self.temps = np.array([])
        self.speed = np.array([])
        self.max_rate = 0

class ht_channel:
    def __init__(self):
        self.sr_duration = dt.time()  # stress relive duration
        self.ht = ht_cl_curve()
        self.cl = ht_cl_curve()
        self.ref_points = dict({})

class ht_chart:
    def __init__(self):
        self.oven_start_load_temp = -1
        self.channel = {'Top': ht_channel(), 'Btn': ht_channel(), 'Program': ht_channel(), 'Oven': ht_channel()}

# finds critical point for stress releving cycle
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

# returns index of next heating/cooling timepoint for given sorted datetime array
def find_next_hour_point_index (date: np.array, prev_index: "index of previous point"):
    if prev_index ==  -1: # -2 is code for reching and of array
        return -2
    hour_increment = 1
    pp = date[prev_index] #previous point
    next_point = pp.replace(second=0, microsecond=0) + dt.timedelta(hours=hour_increment) # creates next point w/ hour increment and w/o seconds and microsecond
    lager_that_point = date[date >= next_point] #creates list of timepoints starting with given amount of hours and minutes
    if len(lager_that_point)>0:
        point = lager_that_point[0] #picks first point from list
        index = np.argmax(date >= point) #finds index of first point in given datetime array
        return index
    else:
        return -1 #return -1 to include last point of given datetime array

def find_ht_cl_rate(ht_cl_crv: ht_cl_curve, date:  np.array, temp: np.array):
    index = 0
    keep_going = True
    timepoint_date_list = np.array([])
    timepoint_temp_list = np.array([])
    while keep_going:
        timepoint_date_list = np.append(timepoint_date_list, date[index])
        timepoint_temp_list = np.append(timepoint_temp_list, temp[index])
        # print(date[index], ' ', temp[index])
        next_index = find_next_hour_point_index(date, index)
        if next_index >= -1:  # we add -1 to include last point of heating/cooling curve
            index = next_index
        else:
            keep_going = False

    temp_change_rate_list = np.array([])

    for i in range(len(timepoint_temp_list) - 1):
        temp_change_rate = abs(timepoint_temp_list[i] - timepoint_temp_list[i + 1])
        temp_change_rate_list = np.append(temp_change_rate_list, temp_change_rate)

    ht_cl_crv.timepoints = timepoint_date_list
    ht_cl_crv.temps = timepoint_temp_list
    ht_cl_crv.speed = temp_change_rate_list
    ht_cl_crv.max_rate = max(temp_change_rate_list)




#------------------Reading raw data from file------------------
#Selection of file to read
#from tkinter import filedialog
#csv_path = filedialog.askopenfilename()
#data_table = pd.read_csv(filepath_or_buffer=csv_path)
#print(csv_path)

number_of_colums_to_read = 6
chanel_names_list = ['Program','Oven','Top','Btn']
column_names_list = list(chanel_names_list)
column_names_list.insert(0,'Date')
redundant_program_column_name = 'Program1'
column_names_list.insert(2,redundant_program_column_name)
#['Date','Program','Program1','Oven','Top','Btn'] #Names for data columns

file_to_read = '17H030.csv' #csv file name

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



ef_sr_card = ht_card()
ef_sr = ht_chart() #end fittings stress relive chart

ef_sr.oven_start_load_temp = data_table['Oven'][0]
for chnl in ('Top', 'Btn'):
    # Finding significant points on graph
    ef_sr.channel[chnl].ref_points = find_reference_points(data_table, chnl, ef_sr_card)

    # Finding heat rates
    start = ef_sr.channel[chnl].ref_points['heating_start_index']
    end = ef_sr.channel[chnl].ref_points['sr_start_index']
    dates = np.array(data_table['Date'][start: end]) # array of dates
    temps = np.array(data_table[chnl][start: end]) #array of temperatures
    find_ht_cl_rate(ef_sr.channel[chnl].ht, dates, temps)
    # print(chnl,' Heating: ',start,' ',end)

    start = ef_sr.channel[chnl].ref_points['sr_end_index']
    end = ef_sr.channel[chnl].ref_points['cooling_end_index']
    dates = np.array(data_table['Date'][start: end]) # array of dates
    temps = np.array(data_table[chnl][start: end]) #array of temperatures
    find_ht_cl_rate(ef_sr.channel[chnl].cl, dates, temps)
    # print(chnl, ' Cooling: ', start, ' ', end)

    # Finding stress relief duration
    start = ef_sr.channel[chnl].ref_points['sr_end_index']
    end = ef_sr.channel[chnl].ref_points['cooling_end_index']
    ef_sr.channel[chnl].sr_duration = data_table['Date'][ef_sr.channel[chnl].ref_points['sr_end_index']] - data_table['Date'][ef_sr.channel[chnl].ref_points['sr_start_index']]

# ------------------Printing result to console ------------------
tb_text = ''
text = 'Oven load temperature: {:3.0f} F'.format(ef_sr.oven_start_load_temp)
print(text)
tb_text += text + '\n'
for chnl in ('Top', 'Btn'):
    print('Channel: ', chnl, ' Heating up:')
    for i in range(len(ef_sr.channel[chnl].ht.timepoints)):
        print('Time: {0:%H:%M:%S} Temperature: {1:3.1f}'.format(ef_sr.channel[chnl].ht.timepoints[i],ef_sr.channel[chnl].ht.temps[i]))
    text = 'Channel:  {0:3s}  Max heating rate: {1:3.0f} F/hour'.format(chnl,ef_sr.channel[chnl].ht.max_rate)
    print(text)
    tb_text += text + '\n'

    td = ef_sr.channel[chnl].sr_duration
    text = 'Channel: {0} Stress relief duration: {1}'.format(chnl, dt.timedelta(seconds=td.seconds))
    print(text)
    tb_text += text + '\n'

    print('Channel: ', chnl, ' Cooling down:')
    for i in range(len(ef_sr.channel[chnl].cl.timepoints)):
        print('Time: {0:%H:%M:%S} Temperature: {1:3.1f}'.format(ef_sr.channel[chnl].cl.timepoints[i],ef_sr.channel[chnl].cl.temps[i]))

    print('Channel:  {0:3s}  Max cooling rate: {1:3.0f} F/hour'.format(chnl, ef_sr.channel[chnl].cl.max_rate))
# ------------------Plotting the data------------------

#Adding line on graph for each chanel
plt.close('all')
fig, ax = plt.subplots(1)

for i in range(len(chanel_names_list)):
    ax.plot(data_table['Date'], data_table[chanel_names_list[i]], label=chanel_names_list[i])

plt.grid() #turn on grid

plt.legend(chanel_names_list)
plt.xlabel('Date/Time')
plt.ylabel('Temperature, F')

# these are matplotlib.patch.Patch properties
props = dict(facecolor='white', alpha = 1)

# place a text box in upper left in axes coords
ax.text(0.3, 0.5, tb_text, transform=ax.transAxes, verticalalignment='top', bbox=props) #fontsize=14

fig.autofmt_xdate()
plt.show()








