# Sensor Fault Detection Using Hierarchical Clustering


# 1. Installation

  In this project 3rd party libraries are used. List of dependencies are listed below.
  - Pandas                          
  - Numpy                            
  - Datetime                         
  - Matplotlib                        
  - Seaborn     
  - Sklearn
  - Collections 
  - Scipy
  - Math
  - Time
  - SFD_utils*
  - mb_ThdData* </br>
  *These are libraries that are created by developer.
  
  
# 2. Aim of the Project

To build sensor fault detection system on highly critical compressor that has 41 different sensor on it in a refinery process.

# 3. File Descriptions

There are 5 files in this project.</br>
- **177K201_sensorNameList**	is a excel file that has sensor names as a list. This list is used for data fecthing process from company database.</br>
- **sensorData** is a excel file that contains 31 days of sensor data to be used in model testing.</br>
- **SFD_Project.ipynb** is a jupyter notebook. You can find the data analysis and modelling steps in here. At bottom of the notebook you find final application that is running in my companys servers.</br>
- **SFD_utils.py** python file that contaions functions that I used in this project.</br>
- **mb_ThdData.py** python module that I created to fetch data from company database. You can not use that code because you are out of company network.</br>

# 4. The Application
Application fetches last 24 hours of data using **mb_ThdData** module and assumes that all sensor are fine at the start and clusters data based on hierarchical clustring. We call those first clusters as **finger-print of the unit**. After every 8 hours (each one represent one shift) we take newly generated data and we cluster it to compare with finger print to detect any faulty sensor. IF all clusters are the same there is nothing to worry about. If each shifts data is O.K. then application uses newly generated 24 hours of data to produce new finger-print then uses to it to check future data. But if it finds any differences between finger-print clusters and newly generated clusters, application detects and identifies which sensor or sensors are clustered differently and shows them as faulty sensors.</br>
You find the code for application at the bottom of the notebook **SFD_Project.ipynb**
