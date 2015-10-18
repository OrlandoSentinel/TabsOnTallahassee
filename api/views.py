from django.db.models import Q
from rest_framework import generics
from .serializers import (Person, SimplePersonSerializer, FullPersonSerializer,
                          Bill, SimpleBillSerializer, FullBillSerializer,
                          Organization, SimpleOrganizationSerializer, FullOrganizationSerializer,
                          Jurisdiction, JurisdictionSerializer,
                          )


class AllowFieldLimitingMixin(object):
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


class PersonList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = SimplePersonSerializer
    full_serializer_class = FullPersonSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Person.objects.all()

        name = self.request.query_params.get('name', None)
        member_of = self.request.query_params.get('member_of', None)
        ever_member_of = self.request.query_params.get('ever_member_of', None)
        latitude = self.request.query_params.get('latitude', None)
        longitude = self.request.query_params.get('longitude', None)

        if name:
            queryset = queryset.filter(Q(name__icontains=name) |
                                       Q(other_names__name__icontains=name)
                                       )
        if member_of:
            queryset = queryset.member_of(member_of)
        if ever_member_of:
            queryset = queryset.member_of(ever_member_of, current_only=False)
        if latitude and longitude:
            pass                # TODO: geo query
        elif latitude or longitude:
            raise Exception()   # TODO: make meaningful exception

        return queryset


class PersonDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = Person.objects.all()
    serializer_class = FullPersonSerializer
    full_serializer_class = FullPersonSerializer


class OrganizationList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = SimpleOrganizationSerializer
    full_serializer_class = FullOrganizationSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Organization.objects.all()
        return queryset


class OrganizationDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = Organization.objects.all()
    serializer_class = SimpleOrganizationSerializer
    full_serializer_class = FullOrganizationSerializer


class BillList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = SimpleBillSerializer
    full_serializer_class = FullBillSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Bill.objects.all()
        return queryset


class BillDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = Bill.objects.all()
    serializer_class = SimpleBillSerializer
    full_serializer_class = FullBillSerializer



class JurisdictionList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = JurisdictionSerializer
    full_serializer_class = JurisdictionSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Jurisdiction.objects.all()
        return queryset


class JurisdictionDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = Jurisdiction.objects.all()
    serializer_class = JurisdictionSerializer
    full_serializer_class = JurisdictionSerializer
