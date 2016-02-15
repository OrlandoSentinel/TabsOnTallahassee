import datetime
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from opencivicdata.models import Bill


class BillAccumulator:
    def __init__(self, days):
        self.days = days
        bills = self.get_bills_with_actions_since(days)
        self.make_buckets(bills)

    def get_bills_with_actions_since(self, days):
        """ get list of all bills w/ actions in last N days """
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=days)).strftime('%Y%m%d')
        today = today.strftime('%Y%m%d')
        bills = Bill.objects.filter(actions__date__range=(yesterday, today))
        # check created/updated date on root bill?
        return bills

    def make_buckets(self, bills):
        """
            given list of modified bills, return mappings by
            legislator, location, and subject
        """
        # map bills
        self.by_legislator = defaultdict(list)
        self.by_location = defaultdict(list)
        self.by_subject = defaultdict(list)

        for bill in bills:
            for sponsor_id in bill.sponsorships.values_list('person_id', flat=True):
                self.by_legislator[sponsor_id].append(bill)
            for location in bill.extras['places']:
                self.by_location[location].append(bill)
            for subject in bill.subject:
                self.by_subject[subject].append(bill)

    def bills_for_user(self, user):
        """ for a user's interests, get all relevant bills """
        people = user.person_follows.values_list('person_id', flat=True)
        locations = user.location_follows.values_list('location', flat=True)
        topics = user.topic_follows.values_list('topic', flat=True)

        bills = set()
        for person_id in people:
            bills.update(self.by_legislator[person_id])
        for location in locations:
            bills.update(self.by_location[location])
        for topic in topics:
            bills.update(self.by_subject[topic])

        return bills


class Command(BaseCommand):
    help = 'Send emails for all updates in last N days'

    def add_arguments(self, parser):
        parser.add_argument('--week', type=bool, action=store_true,
                            default=False)

    def handle(self, *args, **options):
        week = options['week']

        if week:
            days = 7
            email_freq = 'W'
        else:
            days = 1
            email_freq = 'D'

        # get all modified bills
        bill_accumulator = BillAccumulator(days)

        # email users that get emails on this interval
        for user in User.objects.get(preferences__email_frequency=email_freq):
            bills = bill_accumulator.bills_for_user(user)
            count = len(bills)
            # in transaction
                # create EmailRecord
                # send email (rollback if fail)
