from django.urls import path, include

urlpatterns = [
    path('v1/', include('src.api.v1.urls'))
]