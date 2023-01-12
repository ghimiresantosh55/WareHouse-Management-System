from django.db import connection, connections
from tenant.models import Tenant

def hostname_from_request(request):
    # split on `:` to remove port
    return request.get_host().split(":")[0].lower()
    # return request.get_host()


def tenant_schema_from_request(request):
    hostname = hostname_from_request(request)
    tenants_map = get_tenants_map()
    return tenants_map.get(hostname)


def set_tenant_schema_for_request(request):
    schema = tenant_schema_from_request(request)

    connections['log_db'].cursor().execute(f"SET search_path to {schema}")
    connections['default'].cursor().execute(f"SET search_path to {schema}")
    # with connection.cursor() as cursor:
    #     cursor.execute(f"SET search_path to {schema}")


def get_tenants_map():
    connection.cursor().execute(f"SET search_path to public")
    sub_domains = Tenant.objects.order_by('id').values_list("sub_domain", flat=True)
    schema_names = Tenant.objects.order_by('id').values_list("schema_name", flat=True)
    tenants = dict(zip(sub_domains, schema_names))
    return tenants
    # return {"customer1.example.com": "customer1",
    #         "customer2.example.com": "customer2",
    #         "example.com": "public"}