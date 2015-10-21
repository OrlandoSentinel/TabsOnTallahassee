from opencivicdata.models import (Person,
                                  Membership,
                                  Post,
                                  Organization,
                                  Jurisdiction,
                                  Bill,
                                  VoteEvent,
                                  )
from rest_framework import serializers
from .utils import InlineListField, InlineDictField


class SimpleJurisdictionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Jurisdiction
        exclude = ('division', 'locked_fields')

    division_id = serializers.CharField()


class FullJurisdictionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Jurisdiction
        exclude = ('division', 'locked_fields')

    division_id = serializers.CharField()
    legislative_sessions = InlineListField(exclude=['id', 'jurisdiction_id'])


class SimpleMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        exclude = ('id', 'person', 'created_at', 'updated_at',
                   'extras', 'locked_fields',
                   )

class SimplePersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        exclude = ('locked_fields',)


class FullPersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        exclude = ('locked_fields',)

    memberships = SimpleMembershipSerializer(many=True)

    identifiers = InlineListField(exclude=['id', 'person'])
    other_names = InlineListField(exclude=['id', 'person'])
    contact_details = InlineListField(exclude=['id', 'person'])
    object_links = InlineListField(source='links', exclude=['id', 'person'])
    sources = InlineListField(exclude=['id', 'person'])


BILL_LEG_SESSION_FIELDS = ['name', 'identifier', 'jurisdiction_id']


class SimpleBillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bill
        exclude = ('locked_fields',)

    legislative_session = InlineDictField(include=BILL_LEG_SESSION_FIELDS)

class FullBillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bill
        exclude = ('locked_fields',)

    legislative_session = InlineDictField(include=BILL_LEG_SESSION_FIELDS)
    abstracts = InlineListField(exclude=['id', 'bill'])
    other_titles = InlineListField(exclude=['id', 'bill'])
    other_identifiers = InlineListField(exclude=['id', 'bill'])
    actions = InlineListField(exclude=['id', 'bill'],
                              children={'organization': {'include': ['id', 'classification', 'name']}}
                              )
    # TODO: actions.related_entities
    related_bills = InlineListField(exclude=['id', 'bill'])
    # TODO: related_bills_reverse
    sponsorships = InlineListField(exclude=['id', 'bill'])
    documents = InlineListField(exclude=['id', 'bill'],
                                children={'links': {'exclude': ['id']}},
                                )
    versions = InlineListField(exclude=['id', 'bill'],
                               children={'links': {'exclude': ['id']}},
                               )
    sources = InlineListField(exclude=['id', 'bill'])


class FullVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteEvent
        exclude = ('locked_fields',)

    legislative_session = InlineDictField(include=BILL_LEG_SESSION_FIELDS)

    votes = InlineListField(exclude=['id', 'vote_event'],
                            children={'voter': {'include': ['name', 'id']}}
                            )
    counts = InlineListField(exclude=['id', 'vote_event'])
    sources = InlineListField(exclude=['id', 'vote_event'])

class SimpleVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteEvent
        exclude = ('locked_fields',)

    legislative_session = InlineDictField(include=BILL_LEG_SESSION_FIELDS)


class SimpleOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization


class FullOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
