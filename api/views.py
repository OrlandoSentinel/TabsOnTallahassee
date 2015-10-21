import json
from django.db.models import Q
from rest_framework import generics
from .serializers import (Jurisdiction, SimpleJurisdictionSerializer, FullJurisdictionSerializer,
                          Person, SimplePersonSerializer, FullPersonSerializer,
                          Bill, SimpleBillSerializer, FullBillSerializer,
                          VoteEvent, SimpleVoteSerializer, FullVoteSerializer,
                          Organization, SimpleOrganizationSerializer, FullOrganizationSerializer,
                          )
from .utils import AllowFieldLimitingMixin


class JurisdictionList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = SimpleJurisdictionSerializer
    full_serializer_class = FullJurisdictionSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Jurisdiction.objects.all()
        return queryset


class JurisdictionDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = Jurisdiction.objects.all()
    serializer_class = FullJurisdictionSerializer
    full_serializer_class = FullJurisdictionSerializer


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

        session = self.request.query_params.get('legislative_session', None)
        subject = self.request.query_params.get('subject', None)
        extras = self.request.query_params.get('extras', None)
        from_org = self.request.query_params.get('from_organization', None)
        sponsor = self.request.query_params.get('sponsor', None)

        if session:
            queryset = queryset.filter(legislative_session__identifier=session)
        if subject:
            queryset = queryset.filter(subject__contains=[subject])
        if extras:
            try:
                extras = json.loads(extras)
            except ValueError:
                pass
            queryset = queryset.filter(extras__contains=extras)
        if from_org:
            queryset = queryset.filter(from_organization__name=from_org)
        if sponsor:
            queryset = queryset.filter(sponsorships__name=sponsor)

        return queryset


class BillDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    queryset = Bill.objects.all()
    serializer_class = FullBillSerializer
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
