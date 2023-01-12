from django.urls import path

from .views import PackLocationRetrieveApiView, UpdatePackTypeCodeLocationApiView, PackTypeInfoRetrieveApiView, \
    PackCodeDetailInfoRetrieveView

listing_urls = [
    path("pack-code-location/<str:pack_code>", PackLocationRetrieveApiView.as_view()),
    path("pack-code-info/<str:pack_code>", PackTypeInfoRetrieveApiView.as_view()),
    path("serial-no-info/<str:item_serial_no_code>", PackCodeDetailInfoRetrieveView.as_view()),

]
urlpatterns = [
                  path("update-pack-location", UpdatePackTypeCodeLocationApiView.as_view()),
              ] + listing_urls
