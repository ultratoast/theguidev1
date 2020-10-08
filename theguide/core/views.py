from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, authentication, views, response
from rest_framework.renderers import JSONRenderer
from rest_framework.pagination import PageNumberPagination
from theguide.user.perms import *
import django.http,urllib.parse
from django.utils import timezone
from .serializers import *
from .models import *
from .search import *
#from django.db.models import Q
#from django.db.models.functions import Greatest
#from django.db.models.functions import Coalesce,Cast
from django.core.paginator import Paginator
from django.utils.functional import cached_property

class ModuleViewset(viewsets.ModelViewset):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwnerOrReadOnly]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer

    # def list(self, request):
    #     permission_classes = [permissions.IsAuthenticated]
    #     queryset = Module.objects.all()
    #     serializer_class = ModuleSerializer(queryset, many=True)
    #     return response.Response(serializer.data)

    # def retrieve(self, request, pk=None):
    #     permission_classes = [permissions.IsAuthenticated]
    #     queryset = Module.objects.all()
    #     module = get_object_or_404(queryset, pk=pk)
    #     serializer_class = ModuleSerializer(module)
    #     return response.Response(serializer.data)

    # def create(self, request, pk=None):


class ModuleTypeList(generics.ListAPIView):
    queryset = ModuleType.objects.filter(level=0,lft=1).order_by('name')
    serializer_class = ModuleTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    # pagination_class = None

class ModuleSearchList(generics.ListAPIView):

    def list(self, request):
        permission_classes = [permissions.IsAuthenticated]
        searchlist = [Q(title__icontains=request.query_params.get('searchtext','')),Q(description__icontains=request.query_params.get('searchtext',''))]
        queryset = Module.objects.exlude(activated=None).filter(geolocation_lte=request.query_params.get('maxdistance',10),activated_lte=timezone.localtime(timezone.now())).filter(reduce(operator.or_,searchlist))
        serializer_class = ModuleSearchSerializer(queryset, many=True)