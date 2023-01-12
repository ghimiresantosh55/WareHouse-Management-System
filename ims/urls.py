"""pims_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from ims import settings

# import debug_toolbar

schema_view = get_schema_view(
    openapi.Info(
        title="Classic Warehouse Management System",
        default_version='v1',
        description="This is full fledged wms designed for use in multiple warehouses of Classic,Simara",
        terms_of_service="",
        contact=openapi.Contact(email="dipen.2052@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# @login_required
# def protected_serve(request, path, document_root=None, show_indexes=False):
#     return Response({'login_required': 'please login to the site'})
#     return serve(request, path, document_root, show_indexes)


urlpatterns = [
                  path('system-admin/', admin.site.urls),
                  path('api-auth/', include('rest_framework.urls')),
                  path('doc', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
                  path('api/', include('src.api.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
