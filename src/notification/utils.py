from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from django.template.defaultfilters import slugify
from jwt import decode as jwt_decode
from rest_framework import status
from rest_framework.response import Response
from tenant.utils import get_tenants_map
from .models import NotificationGroup


def switch_schema(scope):
    headers = scope['headers']

    arr = dict(headers)

    url = arr[b'host'].decode('utf-8')
    sub_domain = url.split(':')[0]

    schema_map = get_tenants_map()
    schema_name = schema_map.get(sub_domain)

    with connection.cursor() as cursor:
        cursor.execute(f'set search_path to {schema_name}')


@database_sync_to_async
def get_user(scope):

    query_string = parse_qs(scope['query_string'])

    query = dict(query_string).get(b'Token')
    try:

        token = query[0].decode('utf-8')

        decoded_data = jwt_decode(
            token, settings.SECRET_KEY, algorithms=["HS256"])

        switch_schema(scope)

        user = get_user_model().objects.get(id=decoded_data['user_id'])

        return user
    except KeyError as e:
        return Response("You are not logged in !", status=status.HTTP_401_UNAUTHORIZED)


@database_sync_to_async
def get_group_name(user, scope):

    switch_schema(scope)

    try:
        group = NotificationGroup.objects.get(user=user)
    except NotificationGroup.DoesNotExist:
        username = slugify(user.user_name)
        group_name = f'notifications_{user.pk}_{username}'
        group = NotificationGroup.objects.create(user=user,
                                                 group_name=group_name)

    return group

