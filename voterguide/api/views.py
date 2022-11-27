from rest_framework import viewsets

from voterguide.api.models import Candidate, Endorser, Measure, MeasureEndorsement, Seat
from voterguide.api.serializers import (
    CandidateSerializer,
    EndorserSerializer,
    MeasureEndorsementSerializer,
    MeasureSerializer,
    SeatSerializer,
)


class CandidateViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """

    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer


class EndorserViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """

    queryset = Endorser.objects.all()
    serializer_class = EndorserSerializer


class MeasureViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """

    queryset = Measure.objects.all()
    serializer_class = MeasureSerializer


class SeatViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """

    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class MeasureEndorsementViewSet(viewsets.ModelViewSet):
    """
    This viewset provides `list`, `create`, `retrieve`, `update` and `destroy` actions.
    """

    queryset = MeasureEndorsement.objects.all()
    serializer_class = MeasureEndorsementSerializer
