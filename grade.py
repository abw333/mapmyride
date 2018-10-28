import io
import matplotlib
import os
import pandas
import requests
import shutil

#ROUTE_ID = 2292646141
#ROUTE_NAME = 'Cubuy A, B 20181027'

ROUTE_ID = 2238053443
ROUTE_NAME = 'Cerro Punta Elite 20181208'

MINIMUM_DISTANCE_DELTA = 100
GRADE_INTERVAL_BOUNDARIES = (
    -float('inf'), -.5, -.4, -.3, -.2, -.15, -.1, -.08, -.06, -.04, -.02,
     0, .02, .04, .06, .08, .1, .15, .2, .3, .4, .5, float('inf')
)
GRAPHS_DIRECTORY_NAME = 'graphs'

matplotlib.use('TkAgg')

graphs_directory_path = os.path.join(os.path.dirname(__file__), GRAPHS_DIRECTORY_NAME)

try:
    shutil.rmtree(graphs_directory_path)
except FileNotFoundError:
    pass

os.mkdir(graphs_directory_path)

route_csv = requests.get(f'https://www.mapmyride.com/routes/{ROUTE_ID}.csv').text

points = pandas.read_csv(io.StringIO(route_csv)) \
    [['Distance from start(meters)', 'elevation(meters)']] \
    .rename(columns={'Distance from start(meters)': 'distance', 'elevation(meters)': 'elevation'}) \
    .drop_duplicates('distance') \
    .reset_index(drop=True)

points = points[(points['distance'] == 0) | (points['distance'].diff() >= MINIMUM_DISTANCE_DELTA)] \
    .reset_index(drop=True)

deltas = points.diff().rename(columns={'distance': 'distance delta', 'elevation': 'elevation delta'})

points = pandas.concat([points, deltas], axis=1)

points['grade'] = points['elevation delta'] / points['distance delta']

points['grade interval'] = pandas.cut(points['grade'], GRADE_INTERVAL_BOUNDARIES)

distance_by_grade = points.groupby('grade interval')['distance delta'].sum()

distance_by_grade.plot.bar()
matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{ROUTE_NAME} - Distance by Grade.png'))

points.plot('distance', 'grade')
matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{ROUTE_NAME} - Grade by Point.png'))
