import ipinfo
from django.conf import settings
from device_detector import SoftwareDetector
from log_app.models import UserAccessLog
from log_app.serializers.user import UserLoginLogSerializer
from rest_framework import status
from rest_framework.response import Response
def get_ip_details(ip_address=None):
    ipinfo_token = getattr(settings, "IPINFO_TOKEN", None)
    ipinfo_settings = getattr(settings, "IPINFO_SETTINGS", {})
    ip_data = ipinfo.getHandler(ipinfo_token, **ipinfo_settings)
    ip_data = ip_data.getDetails(ip_address)
    return ip_data


def save_user_log(request, user_id):
    ip_data = get_ip_details(request.META.get('REMOTE_ADDR')).all
    # ip_data = get_ip_details('202.51.76.196').all # test ip address
    ip_address = request.META.get('REMOTE_ADDR')

    # getting device info using device_detector library
    user_agent = request.META.get('HTTP_USER_AGENT')
    device = SoftwareDetector(user_agent).parse()

    ipv4_address = ""
    ipv6_address = ""
    if len(str(ip_address)) <= 16:
        ipv4_address = ip_address
    else:
        ipv6_address = ip_address

    # Save User login log data
    if 'bogon' not in ip_data.keys():
        user_log_data = {
            'user_id': user_id,
            'access_type': 1,   # choice field 1 -> Login
            'ipv4_address': ipv4_address,
            'ipv6_address': ipv6_address,
            'access_location': f"{ip_data['city']}, {ip_data['region']}, {ip_data['country_name']}",
            'browser': device.client_name(),
            'browser_version': device.client_version(),
            'platform': device.os_name(),
            'mobile': False,    # slower performance issue to detect device info
            'robot': False,     # to detect bot performance becomes less
            'access_coordinate_la': ip_data['latitude'],
            'access_coordinate_lo': ip_data['longitude'],
        }
    else:
        user_log_data = {
            'user_id': user_id,
            'access_type': 1,  # choice field 1 -> Login
            'ipv4_address': ipv4_address,
            'ipv6_address': ipv6_address,
            'access_location': f"",
            'browser': device.client_name(),
            'browser_version': device.client_version(),
            'platform': device.os_name(),
            'mobile': False,  # slower performance issue to detect device info
            'robot': False,  # to detect bot performance becomes less
            'access_coordinate_la': "",
            'access_coordinate_lo': "",
        }
    user_log_serializer = UserLoginLogSerializer(data=user_log_data)
    if user_log_serializer.is_valid(raise_exception=True):
        user_log_serializer.save()
    else:
        return Response(user_log_serializer.errors, status=status.HTTP_400_BAD_REQUEST)