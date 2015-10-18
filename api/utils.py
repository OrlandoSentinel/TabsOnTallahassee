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
