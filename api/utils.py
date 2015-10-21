from rest_framework import serializers


class AllowFieldLimitingMixin:
    """
    A mixin for a generic APIView that will allow the serialized fields to be
    limited to a set of comma-separated values, specified via the `fields`
    query parameter.  This will only apply to GET requests.

    Must specify a full_serializer_class as well as a serializer_class so
    all fields have a known serialization.
    """
    _serializer_class_for_fields = {}

    def get_serializer_class_for_fields(self, serializer_class, fields):
        fields = sorted(fields.strip().split(','))
        fields = tuple(fields)
        if fields in self._serializer_class_for_fields:
            return self._serializer_class_for_fields[fields]
        # Doing this because a simple copy.copy() doesn't work here.
        meta = type('Meta', (serializer_class.Meta, object), {'fields': fields})
        meta.exclude = []
        LimitedFieldsSerializer = type('LimitedFieldsSerializer', (serializer_class,),
            {'Meta': meta})
        self._serializer_class_for_fields[fields] = LimitedFieldsSerializer
        return LimitedFieldsSerializer

    def get_serializer_class(self):
        """
        Allow the `fields` query parameter to limit the returned fields
        in list and detail views.  `fields` takes a comma-separated list of
        fields.
        """
        fields = self.request.query_params.get('fields')
        if self.request.method == 'GET' and fields:
            return self.get_serializer_class_for_fields(self.full_serializer_class, fields)
        return self.serializer_class


def django_obj_to_dict(obj, include=None, exclude=None, children=None,
                       parent=None, depth=1):
    if obj is None:
        return None
    if exclude is None:
        exclude = []
    if children is None:
        children = {}
    if include:
        included_fields = [f for f in obj._meta.get_fields() if f.name in include]
    else:
        included_fields = [f for f in obj._meta.get_fields() if f.name not in exclude]
    od = {}
    for f in included_fields:
        if f.is_relation:
            if depth <= 0:
                continue
            if f.one_to_many:
                od[f.name] = [django_obj_to_dict(child,
                                                 children.get(f.name, {}).get('include',[]),
                                                 children.get(f.name, {}).get('exclude',[]),
                                                 children.get(f.name, {}).get('children', {}),
                                                 obj,
                                                 depth-1
                                                 )
                              for child in getattr(obj, f.name).all()
                              ]
            elif f.many_to_one:
                child = getattr(obj, f.name)
                if child == parent:
                    continue
                od[f.name] = django_obj_to_dict(child,
                                                children.get(f.name, {}).get('include',[]),
                                                children.get(f.name, {}).get('exclude',[]),
                                                children.get(f.name, {}).get('children', {}),
                                                obj,
                                                depth-1
                                                )
            else:
                import ipdb; ipdb.set_trace()
                raise Exception('unknown relation: ' + f.name)
        else:
            od[f.name] = getattr(obj, f.name)
    return od


class InlineListField(serializers.ListField):
    def __init__(self, *args, **kwargs):
        self.include = kwargs.pop('include', [])
        self.exclude = kwargs.pop('exclude', [])
        self.children = kwargs.pop('children', {})
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        return [django_obj_to_dict(i, self.include, self.exclude, self.children)
                for i in obj.all()]


class InlineDictField(serializers.DictField):
    def __init__(self, *args, **kwargs):
        self.include = kwargs.pop('include', [])
        self.exclude = kwargs.pop('exclude', [])
        self.children = kwargs.pop('children', {})
        super().__init__(*args, **kwargs)

    def to_representation(self, obj):
        return django_obj_to_dict(obj, self.include, self.exclude, self.children)
