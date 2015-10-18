from django.db.models import Q
from rest_framework import generics
from .serializers import (Person, SimplePersonSerializer, FullPersonSerializer,
                          Bill, SimpleBillSerializer, FullBillSerializer,
                          VoteEvent, SimpleVoteSerializer, FullVoteSerializer,
                          Organization, SimpleOrganizationSerializer, FullOrganizationSerializer,
                          Jurisdiction, JurisdictionSerializer,
                          )
from .utils import AllowFieldLimitingMixin


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


class VoteList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = SimpleVoteSerializer
    full_serializer_class = FullVoteSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = VoteEvent.objects.all()
        return queryset


class VoteDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = VoteEvent.objects.all()
    serializer_class = SimpleVoteSerializer
    full_serializer_class = FullVoteSerializer


