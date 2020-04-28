from sklearn import cluster
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, ward, single, fcluster, complete, average
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from sklearn import preprocessing
import datetime


def scalesData(df,is_normalize=False,is_standardize=False):

    """
    Sets Timestamp as Index,
    Normalize data,
    Returns scaled data.

    Parameters:
    df (pandas dataframe): Input data
    is_normalize (boolean)
    is_standardize (boolean)

    Returns:
    df_scaled (pandas dataframe): Normalized or standardized dataframe with timestamp.
    """

    #If there is a timestamp column separete before scaling
    if ('Zaman' in df.columns):
        timestamp = df['Zaman']
        df_values = df.drop(axis='columns',columns=['Zaman'])

    #Normalize dataframe
    if is_normalize:
        # Get column names first
        names = df_values.columns
        #Get scaled array
        df_scaled = preprocessing.normalize(df_values)
        #Create dataframe
        df_scaled = pd.DataFrame(df_scaled, columns=names)
    else:
    #Standardize dataframe
        # Get column names first
        names = df_values.columns
        # Create the Scaler object
        scaler = preprocessing.StandardScaler()
        # Fit your data on the scaler object
        df_scaled = scaler.fit_transform(df_values)
        #Create scaled dataframe
        df_scaled = pd.DataFrame(df_scaled, columns=names)

    df_scaled.insert(0, 'Timestamp', timestamp)

    return df_scaled

def splitsTransposeData(df, n):
    """
    Returns evenly splitted and transposed 'n' number of dataframes.

    Parameters:
    df (pandas dataframe): Input data Should be scaled
    n (integer): number of split

    Returns:
    df_list_T (list of dataframes): List of transposed dataframes.
    """
    #Get number of rows in the df
    n_rows_df= df.shape[0]

    #Create empty list to store dataframes
    df_list_T = []

    for i in range(n):
        #Slice dataframe
        df_slice=df.loc[i*n_rows_df/n:(i+1)*n_rows_df/n]

        #Take transpose
        df_slice_T = np.transpose(df_slice)

        #Get timestamp row and make it column name
        df_slice_T.columns = df_slice_T.iloc[0]
        df_slice_T = df_slice_T[1:]

        #append this sliced dataframe
        df_list_T.append(df_slice_T)

    return df_list_T

def returnSensorClusters(df,clust):
    """
    Returns clusters labels for every sensor

    Parameters:
    df (DataFrame): Dataframes that contains sensor data
    clust (Agglomerative Hierarchical Clustring instance): HC instance that has predefined number of cluster and linkage method.

    Returns:
    finger_print (Series): Series that contains sensors names as index cluster as value
    """

    #get cluster labels
    labels = clust.fit_predict(df)
    #create new series with these labels
    finger_print = pd.Series(data=labels, index=df.index)

    return finger_print.sort_values()

def returnDifferentClusteredTags(series1, series2):

    """
    Returns differences of two series. It gives faulty sensor.

    Parameters:
    series1 (Series): Pandas series that represents sensor and their cluster label
    series2 (Series): Pandas series that represents sensor and their cluster label

    Returns:
    diff (list): List of faulty sensors.
    """

    #Check for differences if there is only 1 difference it is ok
    diffs = list(series1[np.invert(series1.eq(series2))].index.values)

    #If there is more than one differences it means cluster labels are rotated.
    if len(diffs) > 1:
        diffs = list(series1[(series1.eq(series2))].index.values)

    list_remove = []
    for diff in diffs:
        if (diff == '177KI2025.PV') or(diff == '177KI2030.PV'):
            list_remove.append(diff)

    for i in list_remove:
        diffs.remove(i)

    return diffs

def plotComparisionPlot(df1,df2,i):

    """
    Plots two line chart and one dendogram that represents faulty state to compare two different state of the unit .(i.e. finger_print and unit_state)

    Parameters:
    df1 (dataframe): dataframe that represent finger print (needs to be transposed before plotting)
    df2 (dataframe): dataframe that represent faulty unite state (needs to be transposed before plotting)
    i (integer): represents dataframe index
    """


    #To plot we need to make columns as sensor rows as data points
    df_plot_finger = np.transpose(df1)
    df_plot_current = np.transpose(df2)
    #Reset index timestamp to change its data type
    df_plot_finger.reset_index(inplace=True)
    df_plot_current.reset_index(inplace=True)
    #Change its data type to datatime
    df_plot_finger['Timestamp'] = pd.to_datetime(df_plot_finger['Timestamp'])
    #Get start and end date
    start_date_finger_print = str(df_plot_finger['Timestamp'].min())
    end_date_finger_print = str(df_plot_finger['Timestamp'].max())

    df_plot_current['Timestamp'] = pd.to_datetime(df_plot_current['Timestamp'])
    #Get start and end date
    start_date_current= str(df_plot_current['Timestamp'].min())
    end_date_current = str(df_plot_current['Timestamp'].max())
    #make it index again
    df_plot_finger.set_index('Timestamp', inplace=True)
    df_plot_current.set_index('Timestamp', inplace=True)

    #Plot df
    fig, axes = plt.subplots(nrows=1,ncols=3, figsize=(18,10))
    axes[0].set_title('Finger Print (Temperature & Vibration)\n {} - {}'.format(start_date_finger_print, end_date_finger_print))
    axes[0].plot(df_plot_finger.iloc[:,2:])

    axes[1].plot(df_plot_current.iloc[:,2:])
    axes[1].set_title('Current State (Temperature & Vibration)\n {} - {}\n INDEX = {}'.format(start_date_current, end_date_current, i))

    #plot dendrogram of the current-State
    #linkage-matrix for the current-state
    df2_drop=df2.drop(axis='index',index=['177KI2025.PV', '177KI2030.PV'])
    likage = single(df2_drop)
    dendrogram(likage,labels=df2_drop.index,orientation='left',ax=axes[2],distance_sort='descending');
    axes[2].set_title('Faulty Dendrogram');


    plt.show()

def plotComparisionPlot2(df1,df2):

    """
    Plots 2 plot to compare 2 different state of the unit.(i.e. finger_print and unit_state)

    Parameters:
    df1 (dataframe): dataframe that needs to be transposed before plotting
    df2 (dataframe): dataframe that needs to be transposed before plotting
    """
    #To plot we need to make columns as sensor rows as data points
    df_plot_finger = np.transpose(df1)
    df_plot_current = np.transpose(df2)
    #Reset index timestamp to change its data type
    df_plot_finger.reset_index(inplace=True)
    df_plot_current.reset_index(inplace=True)
    #Change its data type to datatime
    df_plot_finger['Timestamp'] = pd.to_datetime(df_plot_finger['Timestamp'])
    #Get start and end date
    start_date_finger_print = str(df_plot_finger['Timestamp'].min())
    end_date_finger_print = str(df_plot_finger['Timestamp'].max())

    df_plot_current['Timestamp'] = pd.to_datetime(df_plot_current['Timestamp'])
    #Get start and end date
    start_date_current= str(df_plot_current['Timestamp'].min())
    end_date_current = str(df_plot_current['Timestamp'].max())
    #make it index again
    df_plot_finger.set_index('Timestamp', inplace=True)
    df_plot_current.set_index('Timestamp', inplace=True)

    #Plot df
    fig, axes = plt.subplots(nrows=1,ncols=2, figsize=(16,4))
    axes[0].set_title('Finger Print (Temperature & Vibration)\n {} - {}'.format(start_date_finger_print, end_date_finger_print))
    axes[0].plot(df_plot_finger.iloc[:,2:])

    axes[1].plot(df_plot_current.iloc[:,2:])
    axes[1].set_title('Current State (Temperature & Vibration)\n {} - {}'.format(start_date_current, end_date_current))
    plt.show()

def healthCheck(list_of_dfs, finger_print, finger_print_df ,clust):
    """
    Compares every dataframe with finger print to detect sensor fault.

    Parameters:
    list_of_dfs (DataFrame): List of dataframes to compare with finger print. Must be normalized and transposed.
    finger_print (Series): Units finger print that represents every sensors cluster
    finger_print_df (DataFrame) : Dataframe that represents finger print (For visual purposes.)
    clust (Agglomerative Hierarchical Clustring instance): HC instance that has predefined number of cluster and linkage method.
    """
    #Get number of df that we have
    numberOfDFs = len(list_of_dfs)

    #Loop every df, get clusters for each df and compare it with finger_print cluster
    for i in range(numberOfDFs):
        if i == 0:
            pass
        else:
            #Get unit state clusters
            unit_state = returnSensorClusters(list_of_dfs[i],clust)
            #Compare this unit state with finger_print
            if finger_print.equals(unit_state):
                pass
            else:
                #Print which sensor is faulty.
                faultySensorList = returnDifferentClusteredTags(finger_print, unit_state)
                print("Faulty sensors detected = {}".format(faultySensorList))

                ##PLOTTING
                plotComparisionPlot(finger_print_df,list_of_dfs[i],i)

def plotSimpleDendogram(df,linkage):
    """
    Plot simple dendogram

    Parameters:
    df (DataFrame): Transposed and Normalize Dataframes that contains sensor data
    linkage (str): type of linkage e.g. 'ward', 'average', 'complete', 'single'

    """
    plt.figure(figsize=(18,10))

    if linkage == 'average':
        likage = average(df)
    elif linkage == 'ward':
        likage = ward(df)
    elif linkage == 'single':
        likage = single(df)
    elif linkage == 'complete':
        likage = complete(df)

    dendrogram(likage,labels=df.index,orientation='top',distance_sort='descending',leaf_rotation=90,leaf_font_size=12);
    plt.show()

def plotDendogramsLineCharts(df_list, n_rows, n_cols, figsize, linkage):
    """
    Plot simple dendogram and line chart side by side

    Parameters:
    df_list (list of DataFrames): Transposed and Normalize Dataframes that contains sensor data
    n_rows (integer): the number of days you want to plot.
    n_cols (integer):
    figsize (tuple): figure size
    linkage (str):  type of linkage e.g. 'ward', 'average', 'complete', 'single'

    """
    #PLOTTING Dendogram and Line Chart
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=figsize)
    fig.subplots_adjust(wspace=.4)
    for ax, df in zip(axes, df_list):

        #PLOTTING DENDOGRAM
        #Compute linkage matrix
        if linkage == 'average':
            linkage_matrix = average(df)
        elif linkage == 'ward':
            linkage_matrix = ward(df)
        elif linkage == 'single':
            linkage_matrix = single(df)
        elif linkage == 'complete':
            linkage_matrix = complete(df)
        #Get dendrogram
        dendrogram(linkage_matrix,ax=ax[0], labels=df.index,orientation='left')
        ax[0].set_title('Dendogram',fontsize='14')


        ##PLOTTING LINE CHART
        #To plot we need to make columns as sensor rows as data points
        df_plot = np.transpose(df)
        #Reset index timestamp to change its data type
        df_plot.reset_index(inplace=True)
        #Change its data type to datatime
        df_plot['Timestamp'] = pd.to_datetime(df_plot['Timestamp'])
        #Get start date and end date
        start_date= str(df_plot['Timestamp'].min())
        end_date = str(df_plot['Timestamp'].max())
        #make it index again
        df_plot.set_index('Timestamp', inplace=True)

        ax[1].plot(df_plot)
        ax[1].set_title('All Sensors\n {} - {}'.format(start_date,end_date),fontsize='14')
        ax[2].plot(df_plot.iloc[:,2:])
        ax[2].set_title('Temperature & Vibration Sensors\n {} - {}'.format(start_date,end_date),fontsize='14')

def filterDBSCAN(df_T):
    """
    Returns DBSCAN filtered dataframe

    Parameters:
    df_T (dataframe): Process historic data, sensors as rows

    Returns:
    df_f_T (dataframe): Filtered dataframe, sensors as rows.
    """

    #instantiate DBSCAN instance
    db = cluster.DBSCAN(eps=0.1,min_samples=50)

    #Tranpose.
    df = np.transpose(df_T)

    #Fit data
    db.fit(df)

    #Append labels
    df['labels'] = db.labels_

    #Print noise
    print('{} rows clustered as noise.'.format(len(df[df['labels']==-1])))

    #Filter Noise
    df_filtered = df[df['labels'] != -1]

    #Drop labels columns
    df_f = df_filtered.drop(axis='columns',columns=['labels'])

    #Transpose.
    df_f_T = np.transpose(df_f)

    return df_f_T
