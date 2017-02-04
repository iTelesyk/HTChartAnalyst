import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt

#------------------Reading raw data from file------------------
#Selection of file to read
#from tkinter import filedialog
#csv_path = filedialog.askopenfilename()
#df = pd.read_csv(filepath_or_buffer=csv_path)
#print(csv_path)

number_of_colums_to_read = 6
chanel_names_list = ['Program','Oven','Top','Bottom']
column_names_list = list(chanel_names_list)
column_names_list.insert(0,'Date')
redundant_program_column_name = 'Program1'
column_names_list.insert(2,redundant_program_column_name)
#['Date','Program','Program1','Oven','Top','Bottom'] #Names for data columns

file_to_read = '17H008.csv' #csv file name

df = pd.read_csv(file_to_read, usecols=range(number_of_colums_to_read)) #reads raw data from csv file
df.columns = column_names_list
#Delete second column of programm set temperature
del df[redundant_program_column_name]

#------------------Data preparations------------------
# Changing Excel Date/Time format to  Python datetime format
import xlrd
PyDate = pd.Series(df.Date)
#!!! that should be fixed -> it should be the way to treat it as a vector, not a list of individual number
for i in range(len(df.Date)):
    PyDate[i] = xlrd.xldate.xldate_as_datetime(df.Date[i], 0)  # Datemode = 0
df.Date = PyDate

#Heat treatment card magic numbers
min_load_temp = 300 #F - minimal temperature before heat treatment should start
ht_nominal_temp = 1050 #F
ht_nominal_temp_deviation = 25 #F
ht_min_temp = ht_nominal_temp-ht_nominal_temp_deviation
ht_max_temp = ht_nominal_temp+ht_nominal_temp_deviation 
max_heating_rate = 172 #F/hour  #!!!
max_cooling_rate = 172 #F/hour
ht_min_duration_rec = dt.time(hour=3, minute=30)
ht_max_duration_rec = dt.time(hour=4, minute=30)
ht_min_duration_acceptable = dt.time(hour=3)
ht_max_duration_acceptable = dt.time(hour=4)




#------------------Plotting the data------------------

#Adding line on graph for each chanel
for i in range(len(chanel_names_list)):
    plt.plot(df['Date'], df[chanel_names_list[i]], label=chanel_names_list[i])

plt.grid() #turn on grid

plt.legend(chanel_names_list)
plt.xlabel('Date/Time')
plt.ylabel('Temperature, F')


#plt.figure(num=None, figsize=(8, 6)) #changing plot field size
plt.show()








