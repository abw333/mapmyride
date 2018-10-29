import io
import matplotlib
import os
import pandas
import requests
import shutil

ROUTES = (
    (2232377818, 'Corozal A, B 20180908'),
    (2112697084, 'Campamento A, B 20180915'),
    (2248058941, 'Regadera A, B 20180922'),
    (2256532609, '3T A, B 20180929'),
    (2263083622, 'Charco Azul A, B 20181006'),
    (2273520217, 'Cascada Espiritu Santo A, B 20181013'),
    (2283542419, 'La Casita del Negro A, B 20181020'),
    (2292646141, 'Cubuy A, B 20181027'),
    (2299872130, 'Paloma A, B 20181103')
)

MINIMUM_DISTANCE_DELTA = 100
GRADE_INTERVAL_BOUNDARIES = (
    -float('inf'), -.2, -.15, -.1, -.08, -.06, -.04, -.02,
     0, .02, .04, .06, .08, .1, .15, .2, float('inf')
)
GRAPHS_DIRECTORY_NAME = 'graphs'

matplotlib.use('TkAgg')

graphs_directory_path = os.path.join(os.path.dirname(__file__), GRAPHS_DIRECTORY_NAME)

try:
    shutil.rmtree(graphs_directory_path)
except FileNotFoundError:
    pass

os.mkdir(graphs_directory_path)

distance_by_grades = []
for route_id, route_name in ROUTES:
    route_csv = requests.get(f'https://www.mapmyride.com/routes/{route_id}.csv').text

    points = pandas.read_csv(io.StringIO(route_csv)) \
        [['Distance from start(meters)', 'elevation(meters)']] \
        .rename(columns={'Distance from start(meters)': 'distance (meters)', 'elevation(meters)': 'elevation (meters)'}) \
        .drop_duplicates('distance (meters)') \
        .reset_index(drop=True)

    points = points[(points['distance (meters)'] == 0) | (points['distance (meters)'].diff() >= MINIMUM_DISTANCE_DELTA)] \
        .reset_index(drop=True)

    deltas = points.diff().rename(columns={'distance (meters)': 'distance delta (meters)', 'elevation (meters)': 'elevation delta (meters)'})

    points = pandas.concat([points, deltas], axis=1)

    points['grade'] = points['elevation delta (meters)'] / points['distance delta (meters)']

    points['grade interval'] = pandas.cut(points['grade'], GRADE_INTERVAL_BOUNDARIES)

    distance_by_grade = points.groupby('grade interval')['distance delta (meters)'].sum().to_frame('distance (meters)')
    distance_by_grades.append(distance_by_grade.rename(columns={'distance (meters)': f'{route_name} distance (meters)'}))

    plot_title = f'{route_name} - Distance by Grade'
    distance_by_grade.plot.bar(title=plot_title, figsize=[2 * size for size in matplotlib.rcParams['figure.figsize']])
    matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{plot_title}.png'), bbox_inches='tight')
    matplotlib.pyplot.clf()

    plot_title = f'{route_name} - Grade by Distance'
    points.plot('distance (meters)', 'grade', title=plot_title, figsize=[2 * size for size in matplotlib.rcParams['figure.figsize']])
    matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{plot_title}.png'), bbox_inches='tight')
    matplotlib.pyplot.clf()

plot_title = 'Distance by Grade'
pandas.concat(distance_by_grades, axis=1).plot.bar(title=plot_title, figsize=[2 * size for size in matplotlib.rcParams['figure.figsize']])
matplotlib.pyplot.savefig(os.path.join(graphs_directory_path, f'{plot_title}.png'), bbox_inches='tight')
matplotlib.pyplot.clf()
