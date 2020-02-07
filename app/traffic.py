import requests
import csv
import json
import pandas as pd

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

        # data = pd.read_csv(self.traffic_csv_path)
        # print(data)



if __name__ == '__main__':
    traffic = Traffic()
    traffic.download_data()