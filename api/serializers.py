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


class InlineListField(serializers.ListField):
    def __init__(self, *args, **kwargs):
        self.include = kwargs.pop('include', [])
        self.exclude = kwargs.pop('exclude', [])
        super().__init__(*args, **kwargs)

    def _get_fields(self, obj):
        if self.include:
            included_fields = self.include
        else:
            included_fields = [k for k in obj.__dict__.keys()
                               if not k.startswith('_') and k not in self.exclude]
        return {f: getattr(obj, f) for f in included_fields}

    def to_representation(self, obj):
        return [self._get_fields(i) for i in obj]


# person
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
