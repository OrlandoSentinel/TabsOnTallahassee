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
        self.hb1.sponsorships.create(person=self.liz)
        self.hb2.sponsorships.create(person=self.liz)
        self.hb2.sponsorships.create(person=self.jack)
        self.hb3.sponsorships.create(person=self.jack)

        # HB1 - Orlando, gators, Liz
        # HB2 - Tallahasse, school, gators, Liz, Jack
        # HB3 - Orlando, Miami, bees, Jack
        # all actions are today
        today = datetime.datetime.today().strftime('%Y%m%d')
        self.hb1.actions.create(date=today, description='action', order=1, organization=org)
        self.hb2.actions.create(date=today, description='action', order=1, organization=org)
        self.hb3.actions.create(date=today, description='action', order=1, organization=org)

    def test_location_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        # no followed items, nothing back
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, set())

        # one location w/ two
        u.location_follows.create(location='Orlando')
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb1, self.hb3})

        # add second location
        u.location_follows.create(location='Tallahassee')
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb1, self.hb2, self.hb3})

        # Orlando only
        u.location_follows.filter(location='Orlando').delete()
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb2})


    def test_topic_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        # one topic w/ two
        u.topic_follows.create(topic='gators')
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb1, self.hb2})

        # add second topic
        u.topic_follows.create(topic='bees')
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb1, self.hb2, self.hb3})

    def test_sponsor_follows(self):
        u = User.objects.create(username='user')

        # actions in the last day
        ba = BillAccumulator(1)

        u.person_follows.create(person=self.liz)
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb1, self.hb2})

        u.person_follows.create(person=self.jack)
        bills = ba.bills_for_user(u)
        self.assertEquals(bills, {self.hb1, self.hb2, self.hb3})

    # test older actions don't show up
    # test future actions don't show up
