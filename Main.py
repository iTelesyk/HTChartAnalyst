from pandas import DataFrame, read_csv

import matplotlib.pyplot as plt
import pandas as pd
import sys
import matplotlib



#Reading raw data from file

#Selection of file to read
#from tkinter import filedialog
#csv_path = filedialog.askopenfilename()
#df = pd.read_csv(filepath_or_buffer=csv_path)
#print(csv_path)

number_of_colums_to_read = 6
file_to_read = '17H008.csv' #file name
column_names_list = ['Date','Program','Program1','Oven','Top','Bottom'] #Names for data columns

df = pd.read_csv(file_to_read, usecols=range(number_of_colums_to_read)) #returns dataframe
df.columns = column_names_list

#Data preparations

# Changing Excel Date/Time format to  Python datetime format
import xlrd
PyDate = pd.Series(df.Date)
#print (PyDate)

for i in range(len(df.Date)):
    PyDate[i] = xlrd.xldate.xldate_as_datetime(df.Date[i], 0)  # Datemode = 0

df.Date = PyDate
#print (df.Date)

#Delete second column of programm set temperature
del df['Program1']

import matplotlib.pyplot as plt

plt.plot(df['Date'], df['Program'], label = 'Program')
plt.plot(df['Date'], df['Oven'], label = 'Oven')
plt.plot(df['Date'], df['Top'], label = 'Top')
plt.plot(df['Date'], df['Bottom'], label = 'Bottom')

plt.xlabel('Date/Time')
plt.ylabel('Temperature, F')
plt.show()








