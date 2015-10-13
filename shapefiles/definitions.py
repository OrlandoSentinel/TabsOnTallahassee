"""
Configuration describing the shapefiles to be loaded.
"""
from django.contrib.gis.gdal.error import OGRIndexError
from datetime import date
import boundaries
import os

FL_FIPS = '12'
state_fips = {'12': 'FL'}


def tiger_namer(feature):
    global OGRIndexError
    global state_fips

    try:
        fips_code = feature.get('STATEFP')
    except OGRIndexError:
        fips_code = feature.get('STATEFP10')

    try:
        name = feature.get('NAMELSAD')
    except OGRIndexError:
        name = feature.get('NAMELSAD10')

    try:
        geoid = feature.get('GEOID')
    except OGRIndexError:
        geoid = feature.get('GEOID10')

    state_abbrev = state_fips[fips_code].upper()
    name = name.encode('utf8').decode('latin-1')
    resp = u"{0} {1} {2}".format(state_abbrev, name, geoid)
    return resp


def geoid_tiger_namer(feature):
    try:
        geoid = feature.get('GEOID')
    except OGRIndexError:
        geoid = feature.get('GEOID10')
    return geoid



class index_namer(object):
    def __init__(self, prefix):
        self.prefix = prefix
        self.count = 0

    def __call__(self, feature):
        self.count += 1
        return '{0}{1}'.format(self.prefix, self.count)


CENSUS_URL = 'http://www.census.gov/geo/maps-data/data/tiger.html'
LAST_UPDATE = date(2015, 8, 19)
defaults = dict(last_updated=LAST_UPDATE,
                domain='United States',
                authority='US Census Bureau',
                source_url=CENSUS_URL,
                license_URL=CENSUS_URL,
                data_url=CENSUS_URL,
                notes='',
                extra='{}',
               )


boundaries.register('sldl-15',
                    singular='sldl-15',
                    file='sldl/',
                    name_func=tiger_namer,
                    id_func=geoid_tiger_namer,
                    start_date=date(2015, 1, 1),
                    **defaults
                   )

boundaries.register('sldu-15',
                    singular='sldu-15',
                    file='sldu/',
                    name_func=tiger_namer,
                    id_func=geoid_tiger_namer,
                    start_date=date(2015, 1, 1),
                    **defaults
                   )

#boundaries.register('county-13',
#                    singular='county-13',
#                    file='county-13/',
#                    encoding='latin-1',
#                    name_func=tiger_namer,
#                    id_func=geoid_tiger_namer,
#                    start_date=date(2012, 1, 1),
#                    end_date=date(2015, 1, 1),
#                    **defaults
#                   )

#boundaries.register('place-14',
#                    singular='place-14',
#                    file='place-14/',
#                    name_func=tiger_namer,
#                    id_func=geoid_tiger_namer,
#                    start_date=date(2015, 1, 1),
#                    encoding='latin-1',
#                    **defaults
#                   )
