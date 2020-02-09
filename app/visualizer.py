import json
import pandas as pd
import plotly.express as px
from app.traffic import Traffic


class Visualizer:
    @staticmethod
    def load_data() -> dict:
        with open('data/final-stations_with_count.json', encoding='utf-8') as data:
            json_data = json.load(data)
        return json_data

    @staticmethod
    def reformat_data(json_data: dict, date: str) -> list:
        """
        Restructure data to a suitable format for conversion into Pandas dataframe and consequent visualization
        using Plotly.
        :param json_data: json data downloaded using GolemioApiDownloader
        :param date: selected date for visualization that is present in the json_data
        :return: list suitable for conversion into the Pandas dataframe
        """
        new_json_data = [{
            'id': station_id,
            'name': data['name'],
            'latitude': data['location']['lat'],
            'longitude': data['location']['lon'],
            'stop_count': data['count'][date],
        } for station_id, data in json_data.items() if data['location']]
        return new_json_data

    def get_possible_dates(self) -> list:
        """
        Get dates for which there are present stop counts in the json_data downloaded with the GolemioApiDownloader.
        :return: list of the dates
        """
        return list(next(iter(self.load_data().values()))['count'].keys())

    def plot(self, date: str, zoom: int = 7):
        """
        Plot the stop counts for the selected date using Plotly Density Mapbox.
        :param date: the selected date from possible dates
        :param zoom: non-required argument for zooming the default location of the map, 6 by default, use 7 for jupyter
        """
        json_data = self.reformat_data(self.load_data(), date)
        df = pd.DataFrame(json_data)
        max_stop_count = df['stop_count'].max()

        fig = px.density_mapbox(
            data_frame=df, lat='latitude', lon='longitude', z='stop_count', hover_name='name',
            radius=15,  # sets the thickness of each data point in the map
            color_continuous_midpoint=max_stop_count / 2.4,  # value found by testing to provide good visibility of
            # points with low number of stop counts per day
            color_continuous_scale='inferno', mapbox_style="open-street-map",
            center=dict(lat=49.80, lon=15.20), zoom=zoom,  # center the map on the Czech Republic
        )
        fig.show()

    def plot_traffic(self,type: str, zoom: int = 9.5, start_hour: int = 0, end_hour: int = 24, data_path: str = 'data/final_traffic.pkl'):
        """
        Plot either delay, load or flow for the selected hour range using Plotly Density Mapbox and output_col method from Traffic.
        :param type: depending on what you want to plot select either delay, flow or load
        :param zoom: optional parameter for zooming the default location of the map
        :param start_hour: optional parameter for starting hour (inclusive, 0 by default)
        :param end_hour: optional parameter for ending hour (exclusive, 24 by default)
        :param data_path: optional parameter for choosing data path
        """

        df = pd.read_pickle(data_path)
        df = Traffic().output_col(data = df, start = start_hour,end = end_hour,out = type)

        max_output = df['output'].max()
        mean_output = df['output'].mean()

        fig = px.density_mapbox(
            data_frame = df, lat = 'lat', lon = 'lon', z = 'output', hover_name = 'name',
            radius = 20,  # sets the thickness of each data point in the map
            color_continuous_midpoint = max_output / mean_output,
            # points with low number of stop counts per day
            color_continuous_scale = 'inferno', mapbox_style = "open-street-map",
            center = dict(lat = 50.07, lon = 14.41), zoom = zoom,  # center the map on Prague
        )
        fig.show()

if __name__ == '__main__':
    visualizer = Visualizer()
    # print(visualizer.get_possible_dates())
    # visualizer.plot('2020-01-02')
    # visualizer.plot('2019-12-07')
    # visualizer.plot_traffic(type = 'flow')
    # visualizer.plot_traffic(type = 'load', zoom = 8)
    # visualizer.plot_traffic(type = 'delay', start_hour = 10, end_hour = 13)
