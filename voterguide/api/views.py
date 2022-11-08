from rest_framework import viewsets

from voterguide.api.models import Candidate, Endorser
from voterguide.api.serializers import CandidateSerializer, EndorserSerializer


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
