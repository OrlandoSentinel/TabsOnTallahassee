from opencivicdata.models import (Person,
                                  PersonIdentifier,
                                  PersonName,
                                  PersonContactDetail,
                                  PersonLink,
                                  PersonSource,
                                  Membership,
                                  Post,
                                  )
from rest_framework import serializers


# person
class PersonRelatedMixin:
    exclude = ('id', 'person')


class PersonIdentifierSerializer(serializers.ModelSerializer):
    class Meta(PersonRelatedMixin):
        model = PersonIdentifier


class PersonNameSerializer(serializers.ModelSerializer):
    class Meta(PersonRelatedMixin):
        model = PersonName


class PersonContactDetailSerializer(serializers.ModelSerializer):
    class Meta(PersonRelatedMixin):
        model = PersonContactDetail


class PersonLinkSerializer(serializers.ModelSerializer):
    class Meta(PersonRelatedMixin):
        model = PersonLink


class PersonSourceSerializer(serializers.ModelSerializer):
    class Meta(PersonRelatedMixin):
        model = PersonSource


class SimpleMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        exclude = ('id', 'person', 'created_at', 'updated_at',
                   'extras', 'locked_fields',
                   )



class SimplePersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person

    memberships = SimpleMembershipSerializer(many=True)


class FullPersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person

    #memberships = MembershipSerializer(many=True)

    identifiers = PersonIdentifierSerializer(many=True)
    other_names = PersonNameSerializer(many=True)
    contact_details = PersonContactDetailSerializer(many=True)
    links = PersonLinkSerializer(many=True)
    sources = PersonSourceSerializer(many=True)

