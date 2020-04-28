import pandas as pd
import requests
import re
import xml.etree.ElementTree as ET
import datetime as dt
import time
import sys


class ThdData():

    def __init__(self, aggregateType, interval, tag_list="",number_of_days="", start_date = "", end_date = "", file_name=""):
        """
        Parameters:
        aggregateType (str):  IZMIT için ->>> PHD_Average, PHD_Raw vs, RUP için ->>> OPC_Time_Average
        interval (str): "1min" "1h" vs..
        tag_list (list): List of tag names.
        number_of_days (int): Dinamik data çekmek istiyorsan şuan ki tarihten ne kadar geriye gitmeli.
        start_date (str): "2019-10-01T00:00:00" "2018-05-20T00:00:00" 2019-05-18T00:00:00 2019-05-01T00:00:00
        end_date (str): "2019-11-01T00:00:00"
        file_name (str): Taglerin yazılı olduğu excel dosyasının ismi. Uzantıyı yazma.

        """

        self.tag_list = tag_list
        self.start_date = start_date
        self.end_date = end_date
        self.number_of_days = number_of_days
        self.aggregateType = aggregateType
        self.interval = interval
        self.df = pd.DataFrame()
        self.file_name = file_name


    def download(self):
        self.tag_list = self.remove_duplicate_taglist()

        self.df = self.loop_thru()
        return self.df


    def remove_duplicate_taglist(self):
        if self.tag_list == "":
            file_name = self.file_name+'.xlsx'
            taglist_df = pd.read_excel(file_name,sheet_name=0)
            self.tag_list = taglist_df.columns.values.tolist()

        silinecekler = []
        new_taglist = self.tag_list
        for i in new_taglist:
            if i[-2:] == ".1" or i[-2:] == ".2" or i[-2:] == ".3":
                print(i + " tekrar eden tag silindi.")
                silinecekler.append(i)
        for i in silinecekler:
            new_taglist.remove(i)
        return new_taglist



    def Get_data_from_phd(self, tag, start_date, end_date):

        if tag[:4] == 'Root':
            DataSourceName = 'RUP'
            if self.aggregateType == "PHD_Average":
                self.aggregateType = "OPC_Time_Average"
        else:
            if self.aggregateType == "OPC_Time_Average":
                self.aggregateType = "PHD_Average"
            DataSourceName = 'IZMIT'

        url="http://phd/opc/Services/phdwebservice.asmx"
        headers = {'content-type': 'text/xml; charset=utf-8'}
        body = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/"><soapenv:Header/><soapenv:Body><tem:GetTagData><tem:request><tem:TagNameArray><tem:string>'+tag+'</tem:string></tem:TagNameArray><tem:StartDate>'+start_date+'</tem:StartDate><tem:EndDate>'+end_date+'</tem:EndDate><tem:DataSourceName>'+DataSourceName+'</tem:DataSourceName><tem:AggregateType>'+self.aggregateType+'</tem:AggregateType><tem:Interval>'+self.interval+'</tem:Interval></tem:request></tem:GetTagData></soapenv:Body></soapenv:Envelope>'

        response = requests.post(url,data=body,headers=headers)
        rest = response.text.split('</TagName>', 1)[-1]
        rest = rest.split('</DataResponseTag>', 1)[0]
        root = ET.fromstring(rest)
        root.tag
        d = []
        time = []
        for node in root:
            value = node.find('Value')
            timestamp = node.find('TimeStamp')
            time.append(self.getvalueofnode(timestamp).replace("T"," ").replace("Z",""))
            d.append(pd.to_numeric(self.getvalueofnode(value)))
        data = {"Zaman":time, tag: d}
        df = (pd.DataFrame(data))

        if DataSourceName == "RUP":
            cols = df.columns
            col = cols[1]
            col = col[9:-6]
            df.columns = ['Zaman', col]

        return  df #["Value"].tolist()

    def loop_thru(self):

        if self.number_of_days != "":
            sec = self.number_of_days*24*60*60
            self.end_date = ((pd.datetime.now()).strftime("%Y-%m-%dT%H:%M:%S")) #2019-01-01T10:30:00
            self.start_date = (pd.datetime.now() - pd.Timedelta(seconds=sec)).strftime("%Y-%m-%dT%H:%M:%S")

        start = time.time()
        df = pd.DataFrame()
        counter = 1
        index = 0
        number_of_tags = len(self.tag_list)
        for tag in self.tag_list:

            if df.empty:

                df=self.Get_data_from_phd(tag,start_date=self.start_date, end_date=self.end_date)
                #print("{0} yazıldı. ({1}/{2})".format(tag,counter,number_of_tags))
                end2 = time.time()
                #print(str(int(end2-start))+" s")
                # if number_of_tags*end2 < 120:
                #     print("Tahmini bitiş süre: {0} s".format(int(number_of_tags*(end2-start))))
                # else:
                #     print("Tahmini bitiş süre: {0} min".format(int(number_of_tags*(end2-start)/60)))
                # counter+=1
            else:
                new_tag_data = self.Get_data_from_phd(tag,start_date=self.start_date, end_date=self.end_date)
                if new_tag_data.empty:

                    pass
                    # print("\n{0} YAZILAMADI. ({1}/{2})".format(tag,counter,number_of_tags))
                else:
                    df = df.merge(new_tag_data,how="inner",on="Zaman")
                    # if df.empty:
                    #     print("\n{0} YAZILAMADI. Zaman kayması var.({1}/{2})".format(tag,counter,number_of_tags))
                    # # else:
                    # #     print("\n{0} yazıldı. ({1}/{2})".format(tag,counter,number_of_tags))

                end2 = time.time()
                if end2-start < 120:
                    pass
                    #print(str(int(end2-start))+" s")
                else:
                    pass
                    #print(str(int((end2-start)/60))+" min")
                counter+=1

        end = time.time()
        timelapse = int(end - start)

        if timelapse > 120:
            timelapse = int(timelapse/60)
            #print("\nDosyan {} dakikada hazırlandı!".format(timelapse))
        else:
            pass
            #print("\nDosyan {} saniyede hazırlandı!".format(timelapse))

        #print("\nKolon sayısı: {0},\n\nSatır sayısı: {1}".format(df.shape[1], df.shape[0]))

        df['Zaman'] = pd.to_datetime(df['Zaman'], dayfirst=True) #convert its date to datetime

        return df

    def getvalueofnode(self, node):
        """ return node text or None """
        return node.text if node is not None else None


    def split_date(self):
        df = self.df
        df['Zaman'] = pd.to_datetime(df['Zaman'], dayfirst=True) #convert its date to datetime
        df['Date'] = [d.date() for d in df['Zaman']] #extracts date
        df['Time'] = [d.time() for d in df['Zaman']] #extracts time
        originalCols = list(df.columns.values) #extracts column names to change the order of columns
        new_columns = originalCols[-2:] + originalCols[1:-2] #changes columns order
        df = df[new_columns] #assigns new column indeces
        self.df= df

    def write_to_csv(self, file_name):
        df = self.df
        df.to_csv(file_name+".csv", index=False)
