from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from provider.models import Provider
from provider.serializers import ProviderSerializer


class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer


class IsValidProvider(APIView):
    def post(self, request):
        provider_id = request.data.get('provider_id', None)
        if not provider_id:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            Provider.objects.get(provider_id=provider_id)
        except (Provider.DoesNotExist, Provider.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Provider ID"})
        return Response({'success': True})


class IsValidProviderPinCode(APIView):
    def post(self, request):
        provider_id = request.data.get('provider_id', None)
        pin_code = request.data.get('pin_code', None)
        if not provider_id or not pin_code:
            return Response({'success': False, 'error': "Invalid POST data"})
        try:
            Provider.objects.get(provider_id=provider_id, pin_code=pin_code)
        except (Provider.DoesNotExist, Provider.MultipleObjectsReturned):
            return Response({'success': False, 'error': "Invalid Provider ID/PIN Code"})
        return Response({'success': True})
