from django.urls import include, path, re_path
from rest_framework import routers

from src.user.views import ChangePasswordView, UpdateProfileView, UserLoginView, UserLogout, UserRegisterView
from .listing_apis.listing_views import GroupListApiView, DepartmentListApiView
from .views import NewTokenRefreshView, UserViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register("users", UserViewSet)

urlpatterns = [
                  path('register', UserRegisterView.as_view(), name="register"),
                  path('login', UserLoginView.as_view(), name='UserLogin'),
                  path('logout', UserLogout.as_view(), name="logout"),
                  path('login/refresh', NewTokenRefreshView.as_view(), name='token_refresh'),
                  path('change-password/<int:pk>', ChangePasswordView.as_view(),
                       name='auth_change_password'),
                  path('update-profile/<int:pk>', UpdateProfileView.as_view(),
                       name='auth_update_profile'),
                  re_path(r'password-reset/', include('django_rest_resetpassword.urls',
                                                      namespace='password_reset')),
                  path('group-list', GroupListApiView.as_view()),
                  path('department-list', DepartmentListApiView.as_view()),
              ] + router.urls

'''
1 - submit email form       //PasswordResetView.as_view()
2 - email sent success message //PasswordResetDoneView.as_view()
3 - Link to password reset form in email  //PasswordResetConfirmView.as_view()
4 - Password successfully changed message //PasswordResetCompleteView.as_view()
'''
