import io
import matplotlib
import os
import pandas
import requests
import shutil

ROUTES = (
    (2292646141, 'Cubuy A, B 20181027'),
    (2299872130, 'Paloma A, B 20181103'),
    (2238053443, 'Cerro Punta Elite 20181208')
)

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

for route_id, route_name in ROUTES:
    route_csv = requests.get(f'https://www.mapmyride.com/routes/{route_id}.csv').text

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
    matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{route_name} - Distance by Grade.png'), bbox_inches='tight')
    matplotlib.pyplot.clf()

    points.plot('distance', 'grade')
    matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{route_name} - Grade by Point.png'), bbox_inches='tight')
    matplotlib.pyplot.clf()
