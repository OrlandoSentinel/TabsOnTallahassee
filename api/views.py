import json
from django.db.models import Q
from django.db.models import Lookup
from django.db.models.fields import TextField
from rest_framework import generics
from .serializers import (Jurisdiction, SimpleJurisdictionSerializer, FullJurisdictionSerializer,
                          Person, SimplePersonSerializer, FullPersonSerializer,
                          Bill, SimpleBillSerializer, FullBillSerializer,
                          VoteEvent, SimpleVoteSerializer, FullVoteSerializer,
                          Organization, SimpleOrganizationSerializer, FullOrganizationSerializer,
                          )
from .utils import AllowFieldLimitingMixin


@TextField.register_lookup
class Fulltext(Lookup):
    lookup_name = 'ftsearch'

    def as_sql(self, compiler, connection):
        """
            this is a hack, but lets us avoid dropping to raw SQL which
            makes combining w/ other filters impossible

            a flexible implentation would be possible by looking up tsv column
            name based on lhs
        """
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "tsv @@ to_tsquery('english', %s)" % (rhs), params


class JurisdictionList(AllowFieldLimitingMixin, generics.ListAPIView):
    serializer_class = SimpleJurisdictionSerializer
    full_serializer_class = FullJurisdictionSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = Jurisdiction.objects.all()
        return queryset


class JurisdictionDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    """
    Detailed resource for single Jurisdiction object.

    Includes all fields by default, can be limited w/ ``fields`` parameter.
    """
    queryset = Jurisdiction.objects.all()
    serializer_class = FullJurisdictionSerializer
    full_serializer_class = FullJurisdictionSerializer


class PersonList(AllowFieldLimitingMixin, generics.ListAPIView):
    """
    Filterable list of all Person objects.

    * **name** - by name (partial matches included)
    * **member_of** - people that are current members of Organization
    * **ever_member_of** - people that have had known membership in Oganization
    * **latitude, longitude** - must be specified together, filters for individuals
                                currently representing a district including the
                                location in question
    """
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
            queryset = queryset.filter(
                memberships__post__division__geometries__boundary__shape__contains='POINT({} {})'
                .format(longitude, latitude)
            )
        elif latitude or longitude:
            raise Exception()   # TODO: make meaningful exception

        return queryset


class PersonDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    """
    Detailed resource for single Person object.

    Includes all fields by default, can be limited w/ ``fields`` parameter.
    """
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
    """
    Detailed resource for single Organization object.

    Includes all fields by default, can be limited w/ ``fields`` parameter.
    """
    queryset = Organization.objects.all()
    serializer_class = SimpleOrganizationSerializer
    full_serializer_class = FullOrganizationSerializer


class BillList(AllowFieldLimitingMixin, generics.ListAPIView):
    """
    Filterable list of all Bill objects.

    * **legislative_session** - bills within the session identified by this session identifier
    * **subject** - bills with given subject
    * **extras** - bills containing a superset of passed JSON
    * **from_organization** - bills originating in given Organization
                              (exact name or ``ocd-organization`` id)
    * **sponsor** - bills sponsored by given entity
                    (exact name or ``ocd-person``/``ocd-organization`` id)
    """
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
        q = self.request.query_params.get('q', None)

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
            if from_org.startswith('ocd-organization/'):
                queryset = queryset.filter(from_organization_id=from_org)
            else:
                queryset = queryset.filter(from_organization__name=from_org)
        if sponsor:
            if sponsor.startswith('ocd-person/'):
                queryset = queryset.filter(sponsorships__person_id=sponsor)
            elif sponsor.startswith('ocd-organization/'):
                queryset = queryset.filter(sponsorships__organization_id=sponsor)
            else:
                queryset = queryset.filter(Q(sponsorships__name=sponsor) |
                                           Q(sponsorships__person__name=sponsor) |
                                           Q(sponsorships__organization__name=sponsor))
        if q:
            queryset = queryset.filter(versions__links__text__ftsearch=q).distinct()

        return queryset


class BillDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    """
    Detailed resource for single Bill object.

    Includes all fields by default, can be limited w/ ``fields`` parameter.
    """
    queryset = Bill.objects.all()
    serializer_class = FullBillSerializer
    full_serializer_class = FullBillSerializer


class VoteList(AllowFieldLimitingMixin, generics.ListAPIView):
    """
    Filterable list of all Bill objects.

    Available Filters:

    * **voter** - votes where given Person voted (by exact name or ``ocd-person`` id)
    * **option** - votes where ``voter``'s vote was of type ``option`` (must provide ``voter``)
    * **bill** - votes related go a given Bill (by ``ocd-bill`` id)
    * **organization** - votes within a given Organization
                         (by exact name or ``ocd-organization`` id)
    """
    serializer_class = SimpleVoteSerializer
    full_serializer_class = FullVoteSerializer
    paginate_by = 50

    def get_queryset(self):
        queryset = VoteEvent.objects.all()

        voter = self.request.query_params.get('voter', None)
        option = self.request.query_params.get('option', None)
        bill = self.request.query_params.get('bill', None)
        organization = self.request.query_params.get('organization', None)

        if voter:
            if voter.startswith('ocd-person/'):
                q = Q(votes__voter__id=voter)
            else:
                # resolved | unresolved name
                q = Q(votes__voter_name=voter) | Q(votes__voter__name=voter)
            if option:
                q &= Q(votes__option=option)
            queryset = queryset.filter(q)
        elif option:
            raise ValueError('must specify voter w/ option')

        if bill:
            queryset = queryset.filter(bill_id=bill)
        if organization:
            if organization.startswith('ocd-organization/'):
                queryset = queryset.filter(organization_id=organization)
            else:
                queryset = queryset.filter(organization__name=organization)

        return queryset


class VoteDetail(generics.RetrieveAPIView, AllowFieldLimitingMixin):
    """
    Detailed resource for single Vote object.

    Includes all fields by default, can be limited w/ ``fields`` parameter.
    """
    queryset = VoteEvent.objects.all()
    serializer_class = FullVoteSerializer
    full_serializer_class = FullVoteSerializer
