from opencivicdata.models import (Person,
                                  Membership,
                                  Post,
                                  Organization,
                                  Jurisdiction,
                                  Bill,
                                  )
from rest_framework import serializers


class InlineMixin:
    def _get_fields(self, obj):
        if self.include:
            included_fields = self.include
        else:
            included_fields = [k for k in obj.__dict__.keys()
                               if not k.startswith('_') and k not in self.exclude]
        return {f: getattr(obj, f) for f in included_fields}


class InlineListField(serializers.ListField, InlineMixin):
    def __init__(self, *args, **kwargs):
        self.include = kwargs.pop('include', [])
        self.exclude = kwargs.pop('exclude', [])
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        return [self._get_fields(i) for i in obj]


class InlineDictField(serializers.DictField, InlineMixin):
    def __init__(self, *args, **kwargs):
        self.include = kwargs.pop('include', [])
        self.exclude = kwargs.pop('exclude', [])
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        return self._get_fields(obj)


class JurisdictionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Jurisdiction
        exclude = ('division',)

    division_id = serializers.CharField()


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

    identifiers = InlineListField(source='identifiers.all', exclude=['id', 'person_id'])
    other_names = InlineListField(source='other_names.all', exclude=['id', 'person_id'])
    contact_details = InlineListField(source='contact_details.all', exclude=['id', 'person_id'])
    object_links = InlineListField(source='links.all', exclude=['id', 'person_id'])
    sources = InlineListField(source='sources.all', exclude=['id', 'person_id'])


class SimpleBillSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Bill

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

