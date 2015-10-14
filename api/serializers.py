from opencivicdata.models import (Person,
                                  PersonIdentifier,
                                  PersonName,
                                  PersonContactDetail,
                                  PersonLink,
                                  PersonSource)
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


class SimplePersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person


class FullPersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person

    identifiers = PersonIdentifierSerializer(many=True)
    other_names = PersonNameSerializer(many=True)
    contact_details = PersonContactDetailSerializer(many=True)
    links = PersonLinkSerializer(many=True)
    sources = PersonSourceSerializer(many=True)
