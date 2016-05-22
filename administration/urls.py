from django.conf.urls import include, url
from rest_framework import routers

from administration.views import AdminViewSet, ProblemCategoryViewSet, ProblemViewSet, ToiletViewSet,\
    ViewManagers, AddManager, ViewManager, DeleteManager

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'problem-category', ProblemCategoryViewSet)
router.register(r'problem', ProblemViewSet)
router.register(r'toilet', ToiletViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(r'^view_managers/$', ViewManagers.as_view(), name='view_managers'),
    url(r'^view_manager/(?P<manager_id>\d+)/$', ViewManager.as_view(), name='view_manager'),
    url(r'^add_manager/$', AddManager.as_view(), name='add_manager'),
    url(r'^delete_manager(?P<manager_id>\d+)/$', DeleteManager.as_view(), name='delete_manager'),
]
