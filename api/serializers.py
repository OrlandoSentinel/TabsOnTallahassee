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

    identifiers = InlineListField(source='identifiers.all', exclude=['id', 'person_id'])
    other_names = InlineListField(source='other_names.all', exclude=['id', 'person_id'])
    contact_details = InlineListField(source='contact_details.all', exclude=['id', 'person_id'])
    object_links = InlineListField(source='links.all', exclude=['id', 'person_id'])
    sources = InlineListField(source='sources.all', exclude=['id', 'person_id'])


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
    abstracts = InlineListField(source='abstracts.all', exclude=['id', 'bill_id'])
    other_titles = InlineListField(source='other_titles.all', exclude=['id', 'bill_id'])
    other_identifiers = InlineListField(source='other_identifiers.all', exclude=['id', 'bill_id'])
    actions = InlineListField(source='actions.all', exclude=['id', 'bill_id'])
    # actions.organization_id => related
    # actions.related_entities
    related_bills = InlineListField(source='related_bills.all', exclude=['id', 'bill_id'])
    # related_bills_reverse
    sponsorships = InlineListField(source='sponsorships.all', exclude=['id', 'bill_id'])
    documents = InlineListField(source='documents.all', exclude=['id', 'bill_id'])
    # documents.links
    versions = InlineListField(source='versions.all', exclude=['id', 'bill_id'])
    # versions.links
    sources = InlineListField(source='sources.all', exclude=['id', 'bill_id'])


class FullVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteEvent

class SimpleVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteEvent

class SimpleOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization

class FullOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
