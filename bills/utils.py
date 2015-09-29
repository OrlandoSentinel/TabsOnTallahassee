import os
import csv
from functools import reduce
from opencivicdata.models import Bill


def get_all_subjects(billset=None):
    if not billset:
        billset = Bill.objects.all()

    subjects = reduce(lambda a,b: a+b, billset.values_list('subject', flat=True))
    # deduped list
    return sorted(set(subjects))


def get_all_locations():
    with open(os.path.join(os.path.dirname(__file__), '..', 'fl', 'places.csv')) as places:
        place_csv = csv.DictReader(places)
        places = sorted(row['name'] for row in place_csv)
    return places
