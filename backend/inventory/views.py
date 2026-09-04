from rest_framework import viewsets
from config.permissions import IsAdminUser
from .models import Asset
from .serializers import AssetSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        asset_type = self.request.query_params.get('asset_type')
        status_filter = self.request.query_params.get('status')
        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
