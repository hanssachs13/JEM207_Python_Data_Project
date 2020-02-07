import requests
import csv
import json
import pandas as pd
import numpy as np

class Traffic:
    def __init__(self):
        self.traffic_url = 'https://raw.githubusercontent.com/datastory/dpp-prepravni-pruzkumy/master/data_csv/TRAM2014_records.csv'
        self.stops_url = 'http://data.pid.cz/stops/json/stops.json'
        self.traffic_csv_path = 'data/traffic.csv'
        self.traffic_json_path = 'data/traffic.json'
        self.stops_json_path = 'data/stops_pid.json'
        self.final_output_path = 'data/final_traffic.json'

    def download_data(self):
        # get traffic records in csv
        response = requests.get(self.traffic_url)
        if str(response.status_code) != '200':
            raise ConnectionError(f'Request failed with {response.status_code}')
        # save response to file
        with open(self.traffic_csv_path, 'wb') as f:
            f.write(response.content)

        # get stops in json
        response = requests.get(self.stops_url)
        if str(response.status_code) != '200':
            raise ConnectionError(f'Request failed with {response.status_code}')
        # save response to file
        with open(self.stops_json_path, 'wb') as f:
            f.write(response.content)

    def process_traffic(self):
        df_traf = pd.read_csv(self.traffic_csv_path)
        # add StopID column
        stop_id = df_traf['Číslo uzlu zastávky'].astype(str) + "/" + df_traf['Číslo sloupku zastávky'].astype(str)
        df_traf['StopID'] = stop_id
        # add Flow column as sum of passengers entering and exiting
        df_traf['Flow'] = df_traf.apply(lambda x: x['Nástupy1'] + x['Nástupy2'] + x['Výstupy1'] +x['Výstupy2'], axis = 1)
        # add Load column as average of passengers on board before arrival and after departure
        df_traf['Load'] = df_traf.apply(lambda x: (x['PočetPoNástupu1'] + x['PočetPoNástupu2'] + x['PočetPředVýstupem1'] + x['PočetPředVýstupem2'])/2, axis = 1)
        # convert departure data to datetime
        df_traf['Skutečný odjezd'] = pd.to_datetime(df_traf['Skutečný odjezd'], infer_datetime_format = True)
        df_traf['Plánovaný odjezd'] = pd.to_datetime(df_traf['Plánovaný odjezd'], infer_datetime_format = True)
        df_traf['Hour'] = pd.DatetimeIndex(df_traf['Plánovaný odjezd']).hour
        # add Delay columns in seconds
        df_traf['Delay'] = df_traf.apply(lambda x: max((x['Skutečný odjezd'] - x['Plánovaný odjezd'])/np.timedelta64(1,'s'), 0), axis = 1)

        print(df_traf)




if __name__ == '__main__':
    traffic = Traffic()
    # traffic.download_data()
    traffic.process_traffic()