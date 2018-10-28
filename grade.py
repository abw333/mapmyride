import io
import matplotlib
import pandas
import requests

#ROUTE_ID = 2292646141 # Cubuy A, B 20181027
ROUTE_ID = 2238053443 # Cerro Punta Elite 20181208

MINIMUM_DISTANCE_DELTA = 100
GRADE_INTERVAL_BOUNDARIES = (
    -float('inf'), -.5, -.4, -.3, -.2, -.15, -.1, -.08, -.06, -.04, -.02,
     0, .02, .04, .06, .08, .1, .15, .2, .3, .4, .5, float('inf')
)

matplotlib.use('TkAgg')

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

points.plot('distance', 'grade')

matplotlib.pyplot.show()
