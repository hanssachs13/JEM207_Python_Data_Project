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
        self.traffic_ext_csv_path = 'data/traffic_ext.csv'
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
        # create new list
        traf_list = []
        # process csv data by line
        with open(self.traffic_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # skip header
            next(reader, None)
            # for every line
            for row in reader:
                # create new item in list
                traf_list.append({
                    "id": row[14] + "/" + row[15],
                    "realTime": row[2],
                    "schTime": row[3],
                    "entry": int(row[6]) + int(row[7]),
                    "exit": int(row[12]) + int(row[13]),
                    "befArr": int(row[10]) + int(row[11]),
                    "aftDep": int(row[8]) + int(row[9]),
                })

        # sort by id
        traf_list.sort(key = lambda x: x["id"], reverse = False)
        # store in file
        with open("data/traffic_out.json", "w", encoding = 'utf-8') as f:
            json.dump(traf_list, f, ensure_ascii = False, indent = 4)




if __name__ == '__main__':
    traffic = Traffic()
    # traffic.download_data()
    traffic.process_traffic()