import datetime
from collections import defaultdict

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.template.loader import get_template

from opencivicdata.models import Bill
from ...models import EmailRecord


class BillAccumulator:
    def __init__(self, days):
        self.days = days
        bills = self.get_bills_with_actions_since(days)
        print('Accumulated {} bills for {} days...'.format(len(bills), days))
        self.make_buckets(bills)

    def get_bills_with_actions_since(self, days):
        """ get list of all bills w/ actions in last N days """
        today = datetime.date.today()
        yesterday = (today - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        today = today.strftime('%Y-%m-%d')
        bills = Bill.objects.filter(actions__date__range=(yesterday, today))
        # check created/updated date on root bill?

        # annotate bills w/ actions
        for bill in bills:
            bill.latest_action = bill.actions.all().order_by('-order')[0]
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
        parser.add_argument('--week', action='store_true',
                            default=False)

    def handle(self, *args, **options):
        week = options['week']

        if week:
            days = 7
            email_freq = 'W'
            subject = 'Tabs on Tallahasse: Week of {}'.format(
                datetime.date.today().strftime('%B %d, %Y')
            )
        else:
            days = 1
            email_freq = 'D'
            subject = 'Tabs on Tallahasse: {}'.format(
                datetime.date.today().strftime('%B %d, %Y')
            )

        # get all modified bills
        bill_accumulator = BillAccumulator(days)

        # email users that get emails on this interval
        users = User.objects.filter(preferences__email_frequency=email_freq)
        print('{} users to process...'.format(len(users)))
        for user in users:
            bills = bill_accumulator.bills_for_user(user)
            if not bills:
                continue

            # build email message
            text_template = get_template('email/updates.txt')
            text_content = text_template.render({
                'bills': bills,
                'subject': subject,
            })
            msg = EmailMultiAlternatives(subject,
                                            text_content,
                                            settings.DEFAULT_FROM_EMAIL,
                                            [user.email]
                                            )
            # add html if user prefers it
            if user.preferences.email_type == 'H':
                html_template = get_template('email/updates.html')
                html_content = html_template.render({
                    'bills': bills,
                    'subject': subject,
                })
                msg.attach_alternative(html_content, "text/html")

            # send & record sending together
            with transaction.atomic():
                er = EmailRecord.objects.create(
                    user=user,
                    bills=len(bills),
                )
<<<<<<< HEAD
                # if this fails it'll break the transaction & roll it back
=======

                text_template = get_template('email/updates.txt')
                text_content = text_template.render({
                    'bills': bills,
                    'subject': subject,
                    'unsubscribe_guid': er.unsubscribe_guid,
                })
                msg = EmailMultiAlternatives(subject,
                                             text_content,
                                             settings.DEFAULT_FROM_EMAIL,
                                             [user.email]
                                             )
                # add html if user prefers it
                if user.preferences.email_type == 'H':
                    html_template = get_template('email/updates.html')
                    html_content = html_template.render({
                        'bills': bills,
                        'subject': subject,
                        'unsubscribe_guid': er.unsubscribe_guid,
                    })
                    msg.attach_alternative(html_content, "text/html")
>>>>>>> email-unsub
                msg.send()
