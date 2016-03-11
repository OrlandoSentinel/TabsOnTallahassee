import datetime
from django.test import TestCase
from django.contrib.auth.models import User
from opencivicdata.models import (Bill, LegislativeSession, Jurisdiction,
                                  Division, Organization, Person)
from preferences.models import Preferences
from .management.commands.send_email import BillAccumulator


class EmailerTestCase(TestCase):
    def setUp(self):
        div = Division.objects.create(id='ocd-division/country:us/state:fl',
                                      name='Florida')
        juris = Jurisdiction.objects.create(name='Florida', division=div)
        session = LegislativeSession.objects.create(name='2016',
                                                    jurisdiction=juris)
        org = Organization.objects.create(jurisdiction=juris, name='House')
        self.liz = Person.objects.create(name='Liz')
        self.jack = Person.objects.create(name='Jack')

        self.hb1 = Bill.objects.create(
            identifier='HB 1',
            legislative_session=session,
            extras={'places': ['Orlando']},
            subject=['gators'],
        )
        self.hb2 = Bill.objects.create(
            identifier='HB 2',
            legislative_session=session,
            extras={'places': ['Tallahassee']},
            subject=['school', 'gators'],
        )
        self.hb3 = Bill.objects.create(
            identifier='HB 3',
            legislative_session=session,
            extras={'places': ['Orlando', 'Miami']},
            subject=['bees'],
        )
        # this bill hasn't been updated in a month
        self.hb4 = Bill.objects.create(
            identifier='HB 4',
            legislative_session=session,
            extras={'places': ['Orlando', 'Miami']},
            subject=['bees', 'school'],
        )
        # this bill only has updates in the future
        self.hb5 = Bill.objects.create(
            identifier='HB 5',
            legislative_session=session,
            extras={'places': ['Orlando', 'Miami']},
            subject=['bees', 'school'],
        )
        self.hb1.sponsorships.create(person=self.liz)
        self.hb2.sponsorships.create(person=self.liz)
        self.hb2.sponsorships.create(person=self.jack)
        self.hb3.sponsorships.create(person=self.jack)
        self.hb4.sponsorships.create(person=self.jack)
        self.hb5.sponsorships.create(person=self.jack)

        # HB1 - Orlando, gators, Liz
        # HB2 - Tallahasse, school, gators, Liz, Jack
        # HB3 - Orlando, Miami, bees, Jack
        # all actions are today
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        month_ago = (datetime.datetime.today() - datetime.timedelta(days=30)
                     ).strftime('%Y-%m-%d')
        self.hb1.actions.create(date=today, description='action', order=1,
                                organization=org)
        self.hb2.actions.create(date=today, description='action', order=1,
                                organization=org)
        self.hb3.actions.create(date=today, description='action', order=1,
                                organization=org)
        # 4 and 5 are same as 3 but w/ actions at other times
        month_ago = (datetime.datetime.today() - datetime.timedelta(days=30)
                     ).strftime('%Y-%m-%d')
        self.hb4.actions.create(date=month_ago, description='action', order=1,
                                organization=org)
        future = (datetime.datetime.today() + datetime.timedelta(days=30)
                     ).strftime('%Y-%m-%d')
        self.hb5.actions.create(date=future, description='action', order=1,
                                organization=org)

    def test_location_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        # no followed items, nothing back
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, set())

        # one location w/ two
        u.location_follows.create(location='Orlando')
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1, self.hb3})

        # add second location
        u.location_follows.create(location='Tallahassee')
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1, self.hb2, self.hb3})

        # Orlando only
        u.location_follows.filter(location='Orlando').delete()
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb2})


    def test_topic_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        # one topic w/ two
        u.topic_follows.create(topic='gators')
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1, self.hb2})

        # add second topic
        u.topic_follows.create(topic='bees')
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1, self.hb2, self.hb3})

    def test_sponsor_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        u.person_follows.create(person=self.liz)
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1, self.hb2})

        u.person_follows.create(person=self.jack)
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1, self.hb2, self.hb3})

    def test_bill_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        u.bill_follows.create(bill=self.hb1)
        u.bill_follows.create(bill=self.hb4)
        bills = set(ba.bills_for_user(u))
        self.assertEquals(bills, {self.hb1})


    def test_bill_reasons(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        u.person_follows.create(person=self.liz)
        u.bill_follows.create(bill=self.hb1)
        u.topic_follows.create(topic='gators')
        u.location_follows.create(location='Orlando')
        bills = ba.bills_for_user(u)

        self.assertIn(('person', self.liz.name), bills[self.hb1])
        self.assertIn(('bill', self.hb1.id), bills[self.hb1])
        self.assertIn(('location', 'Orlando'), bills[self.hb1])
        self.assertIn(('topic', 'gators'), bills[self.hb1])
