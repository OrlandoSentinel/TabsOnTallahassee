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
    legislative_session = InlineListField(source='legislative_sessions.all',
                                          exclude=['id', 'jurisdiction_id'])


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

    memberships = SimpleMembershipSerializer(many=True)


class FullPersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        exclude = ('locked_fields',)

    #memberships = MembershipSerializer(many=True)

    identifiers = InlineListField(source='identifiers.all', exclude=['id', 'person_id'])
    other_names = InlineListField(source='other_names.all', exclude=['id', 'person_id'])
    contact_details = InlineListField(source='contact_details.all', exclude=['id', 'person_id'])
    object_links = InlineListField(source='links.all', exclude=['id', 'person_id'])
    sources = InlineListField(source='sources.all', exclude=['id', 'person_id'])


class SimpleBillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bill

    legislative_session = InlineDictField()


class FullVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteEvent

    legislative_session = InlineDictField()

class SimpleVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoteEvent

    legislative_session = InlineDictField()


class FullBillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bill


class SimpleOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization

class FullOrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization
