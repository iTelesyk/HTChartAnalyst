from pandas import DataFrame, read_csv

import matplotlib.pyplot as plt
import pandas as pd
import sys
import matplotlib

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
#print (PyDate)

#!!! that should be fixed -> it should be the way to treat it as a vector, not a list of individual number
for i in range(len(df.Date)):
    PyDate[i] = xlrd.xldate.xldate_as_datetime(df.Date[i], 0)  # Datemode = 0

df.Date = PyDate
#print (df.Date)


#------------------Plotting the data------------------
import matplotlib.pyplot as plt

#Adding line on graph for each chanel
for i in range(len(chanel_names_list)):
    plt.plot(df['Date'], df[chanel_names_list[i]], label=chanel_names_list[i])

plt.grid() #turn on grid

plt.legend(chanel_names_list)
plt.xlabel('Date/Time')
plt.ylabel('Temperature, F')
plt.show()








