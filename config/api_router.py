from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from x_factor_be.users.api.views import UserViewSet, CalendarViewset

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("calendar", CalendarViewset)


app_name = "api"
urlpatterns = router.urls
