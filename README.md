# Public transport stop frequency

This project downloads available public transport data about frequency of stops per day by the public transport on all available stops. The data is downloaded from **Golemio API**, "documentation" can be found here: https://golemioapi.docs.apiary.io/. Additionally, it also uses data about the usage of public transport from https://github.com/datastory/dpp-prepravni-pruzkumy combined with data on stops from **PID**.

*The lack of documentation can unfortunately lead to faulty behaviour, and unknown limitations. E.g. It appears, that the data can be downloaded for only 'today' and 10 days in advance. It also appears, that there are no limitations as far as number of data that can be downloaded or number of requests to the API, that can be made.*

```python
from app.downloader import GolemioApiDownloader
from app.traffic import Traffic
from app.visualizer import Visualizer
```
The `GolemioApiDownloader` and `Traffic` can be used for retrieving and reworking the data into a suitable format that is used then for visualizing it with the `Visualizer`.

## GolemioApiDownloader

There are few steps in getting the final data.
1. `download_all_stations()` method. First we need to download info about all the stations.
2. `filter_station_ids_enriched()` method. Then we need to restructure this data to account for parent-child stations and possibly save some memory by keeping only necessary information about the stops.
3. `count_stop_times_per_day()` method. Then we download stop counts (How many times public transport stops at the particular station per selected day.) for all stops from the previous steps for the selected date. This date needs to be in format: YYYY-MM-DD.
4. `assign_stop_count()` method. Finally we can aggregate and assign stop count to only all the parent stations for the selected date. When running this phase for the first time, and not using any previous data, `initial` needs to be set to `True`. When running this step again and having some data already stored from previous runs of this step, then set the `initial` to `False`. This preserves the previous data for other days than the selected. (E.g. We run the 4. step for the first time for 2019-12-20 setting `initial=True`. The resulting output data contains stop counts only for 2019-12-20. We then download stop counts for 2019-12-21 and run the 4. step again selecting this date and `initial=False`. The resulting data contains stop counts for both 2019-12-20 and 2019-12-21.)

All of this steps can be run **individually**. (E.g. We have already downloaded and reworked the data for stations - from steps 1 and 2. And want only to download another day of stop counts. In such case it is sufficient to run just the steps 3 and 4.)

*Bear in mind. Downloading data in the step 3 takes a lot of time, possibly 1/2 hour or more. It may appear as if nothing happens, however the download is running and makes few breaks along the way (printing 'sleeping..' in the console). No timeouts were encountered during the testing.*

**_To make it more comfortable to test this Project, there is already some data present in the repository that can be visualized straight away._**

```python
my_api_key_path = 'golemio_api_key.json'  # path to your Golemio API key
my_date = '2020-01-02'
golemio = GolemioApiDownloader(my_api_key_path)
# golemio.download_all_stations()  # step 1
# golemio.filter_station_ids_enriched()  # step 2
# golemio.count_stop_times_per_day(my_date)  # step 3
# golemio.assign_stop_count(my_date, initial=False)  # step 4
```

## Traffic

The `Traffic` class downloads and processes data about stops and public transport usage. Data can be downloaded and processed in the following steps:
1. `download_data()` method. This dowloads data about stops from PID and traffic data. The current setup downloads and processes traffic data of trams from 2014.
2. `process_traffic()` method. Processes traffic data to prepare for a merge with stops data.
3. `process_stops()` method. Processes stops data to prepare them for a merge with traffic data. 
4. `merge_panda()` method. This method merges data created in steps 2 and 3 so they can be used for visualization.

All of this steps can also be run individually. However, as this is not as time consuming as the methods in `GolemioApiDownloader`, data are not provided and have to be downloaded first.

Additionally, the `Traffic` class also includes the `output_col()` method, which is used by the `Visualizer`. It is not necessary to run this method separately. Based on user selection, it either calculates `delay`, `flow`, or `load` and returns its mean value for each specific station and for the specified hour range.

Delay is calculated as a difference between real and scheduled departure. Early departures are treated as zeroes, i.e. as if the tram was exactly on time.

Flow is the sum of passengers entering and exiting the tram, and represents the number of passengers for which the particular stop is either start, intermediate, of final stop. This gives the user an idea of how busy a particular stop is.

Load is the average of passengers on board before the tram arrives to the stop and after it leaves the stop. It therefore represents how full or empty the tram is at that given station.

```python
traf = Traffic()
traf.download_data()
traf.process_traffic()
traf.process_stops()
traf.merge_panda()
```

## Visualizer

#### Frequency

Visualize the stop counts using plotly and its density mapbox.
First, you can run the method `get_possible_dates()` to see for which dates data is present. Then select the date and visualize it using the `plot()` method (zoom is by default 7 - suitable for opening visualization in a browser. Set to 6 for running in jupyter notebook - or just zoom in/out using the mouse when visualization loads).

*Unfortunately, there seems to an issue with displaying the map in JupyterLab, only a blank rectangle is returned. However, things should work fine in Jupyter Notebook and other programs, such as PyCharm.*

```python
visualizer = Visualizer()
# print(visualizer.get_possible_dates())
visualizer.plot('2020-01-02', zoom=6)
# visualizer.plot('2019-12-07')
```

#### Traffic

To visualize the traffic information (i.e. `delay`, `flow`, or `load`) the user must specify it as parameter `type` within the `plot_traffic()` method. Additionally, users can specify the hour range for which they want to display the information via the `start_hour` (inclusive) and `end_hour` (exclusive) parameters. E.g. if they are interested in the morning traffic they can choose a range from 6 to 9. Information for the full day is returned by default. Zoom is set to 9.5 by default but can be adjusted by the user.

```python
visualizer = Visualizer()
visualizer.plot_traffic(type = 'delay', start_hour = 6, end_hour = 13)
# visualizer.plot_traffic(type = 'flow')
# visualizer.plot_traffic(type = 'load', zoom = 8)
```

Now browse the most and least frequent places across Prague and its surroundings in terms of number of public transport connections per day, as well as the busyness of those stops. :)

*The brightest - most yellow are the most frequent places...*
> Stations are aggregated based on their parent-children relations that come from the Golemio API, not by the name of the stop. Aggregating the stops by their name could make more sense in terms of the aggregated stop count, however, it may be difficult to provide relevant location for the aggregated result. Also, in the current way, it may be possible for some stations to distinguish between different types of transport (bus, subway, tram..)