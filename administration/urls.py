from django.conf.urls import include, url
from rest_framework import routers

from administration.views import AdminViewSet, ProblemCategoryViewSet, ProblemViewSet, ToiletViewSet

router = routers.DefaultRouter()
router.register(r'admin', AdminViewSet)
router.register(r'problem-category', ProblemCategoryViewSet)
router.register(r'problem', ProblemViewSet)
router.register(r'toilet', ToiletViewSet)

urlpatterns = [
    # url(r'^sample/', sample.view, name='sample_name'),
    url(r'^api/', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
