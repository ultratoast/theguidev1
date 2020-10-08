from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from rest_framework.routers import DefaultRouter,SimpleRouter

router = DefaultRouter()
router.register(r'module',views.ModuleViewSet,basename='module')
router.register(r'moduletype',views.ModuleTypeList,basename='moduletype')
router.register(r'modulesearch',views.ModuleSearchList,basename='modulesearch')

urlpatterns = [
    url(r'^', include(router.urls)),
]